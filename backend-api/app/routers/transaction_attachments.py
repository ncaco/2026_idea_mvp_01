from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from app.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.transaction_attachment import TransactionAttachment
from app.services import transaction_attachment_service

router = APIRouter()


@router.get("/transaction/{transaction_id}", response_model=List[TransactionAttachment])
def get_transaction_attachments(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """거래별 첨부파일 목록 조회"""
    return transaction_attachment_service.get_attachments_by_transaction(
        db, transaction_id, current_user.id
    )


@router.post("/transaction/{transaction_id}", response_model=TransactionAttachment, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    transaction_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """첨부파일 업로드"""
    try:
        file_content = await file.read()
        attachment = transaction_attachment_service.create_attachment(
            db,
            transaction_id,
            current_user.id,
            file.filename or 'unknown',
            file_content,
            file.content_type or 'application/octet-stream'
        )
        return attachment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 업로드 실패: {str(e)}"
        )


@router.get("/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """첨부파일 다운로드"""
    attachment = transaction_attachment_service.get_attachment(
        db, attachment_id, current_user.id
    )
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="첨부파일을 찾을 수 없습니다."
        )
    
    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="파일이 존재하지 않습니다."
        )
    
    return FileResponse(
        attachment.file_path,
        media_type=attachment.mime_type,
        filename=attachment.file_name
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """첨부파일 삭제"""
    success = transaction_attachment_service.delete_attachment(
        db, attachment_id, current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="첨부파일을 찾을 수 없습니다."
        )
