from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import os
import uuid
from pathlib import Path

from app.models import TransactionAttachment, Transaction
from app.schemas.transaction_attachment import TransactionAttachmentBase


def get_attachment(db: Session, attachment_id: int, user_id: int) -> Optional[TransactionAttachment]:
    """첨부파일 조회"""
    return db.query(TransactionAttachment).filter(
        and_(
            TransactionAttachment.id == attachment_id,
            TransactionAttachment.user_id == user_id
        )
    ).first()


def get_attachments_by_transaction(db: Session, transaction_id: int, user_id: int) -> List[TransactionAttachment]:
    """거래별 첨부파일 목록 조회"""
    # 거래가 사용자의 것인지 확인
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
    ).first()
    
    if not transaction:
        return []
    
    return db.query(TransactionAttachment).filter(
        TransactionAttachment.transaction_id == transaction_id
    ).all()


def create_attachment(
    db: Session,
    transaction_id: int,
    user_id: int,
    file_name: str,
    file_content: bytes,
    mime_type: str
) -> TransactionAttachment:
    """첨부파일 생성"""
    # 거래가 사용자의 것인지 확인
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
    ).first()
    
    if not transaction:
        raise ValueError("거래를 찾을 수 없습니다.")
    
    # 파일 저장 디렉토리 생성
    BASE_DIR = Path(__file__).parent.parent.parent
    UPLOAD_DIR = BASE_DIR / "uploads" / str(user_id)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # 고유한 파일명 생성
    file_ext = Path(file_name).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # 파일 저장
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    # 데이터베이스에 기록
    attachment = TransactionAttachment(
        transaction_id=transaction_id,
        user_id=user_id,
        file_name=file_name,
        file_path=str(file_path),
        file_size=len(file_content),
        mime_type=mime_type
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def delete_attachment(db: Session, attachment_id: int, user_id: int) -> bool:
    """첨부파일 삭제"""
    attachment = get_attachment(db, attachment_id, user_id)
    if not attachment:
        return False
    
    # 파일 삭제
    if os.path.exists(attachment.file_path):
        try:
            os.remove(attachment.file_path)
        except Exception:
            pass  # 파일 삭제 실패해도 DB 레코드는 삭제
    
    # 데이터베이스에서 삭제
    db.delete(attachment)
    db.commit()
    return True
