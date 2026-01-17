"""
CSV 파일 처리 서비스
"""
from io import BytesIO, StringIO
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal
import csv
from sqlalchemy.orm import Session
from app.models import Transaction, Category


def export_transactions_to_csv(
    db: Session,
    transactions: List[Transaction],
    categories: Dict[int, Category]
) -> BytesIO:
    """
    거래 내역을 CSV 파일로 변환
    
    Args:
        db: 데이터베이스 세션
        transactions: 거래 내역 리스트
        categories: 카테고리 딕셔너리 (category_id -> Category)
    
    Returns:
        BytesIO: CSV 파일 바이트 스트림 (UTF-8 with BOM for Excel compatibility)
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # BOM 추가 (Excel에서 UTF-8 인식)
    output.write('\ufeff')
    
    # 헤더 작성
    headers = ["날짜", "유형", "카테고리", "금액", "설명", "등록일시", "수정일시"]
    writer.writerow(headers)
    
    # 데이터 작성
    for transaction in transactions:
        category = categories.get(transaction.category_id)
        category_name = category.name if category else "알 수 없음"
        
        # 날짜 형식 변환
        transaction_date = transaction.transaction_date
        if isinstance(transaction_date, str):
            transaction_date = datetime.strptime(transaction_date, "%Y-%m-%d").date()
        
        row = [
            transaction_date.strftime("%Y-%m-%d"),
            "수입" if transaction.type == "income" else "지출",
            category_name,
            float(transaction.amount),
            transaction.description or "",
            transaction.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(transaction.created_at, datetime) else str(transaction.created_at),
            transaction.updated_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(transaction.updated_at, datetime) else str(transaction.updated_at),
        ]
        writer.writerow(row)
    
    # StringIO를 BytesIO로 변환
    output.seek(0)
    csv_bytes = BytesIO(output.getvalue().encode('utf-8-sig'))  # UTF-8 with BOM
    csv_bytes.seek(0)
    
    return csv_bytes


def import_transactions_from_csv(
    db: Session,
    file_content: bytes,
    user_id: int,
    categories: Dict[str, Category]  # category_name -> Category
) -> Dict[str, Any]:
    """
    CSV 파일에서 거래 내역을 읽어서 데이터베이스에 저장
    
    Args:
        db: 데이터베이스 세션
        file_content: CSV 파일 바이트
        user_id: 사용자 ID
        categories: 카테고리 딕셔너리 (category_name -> Category)
    
    Returns:
        Dict: {"success": int, "failed": int, "errors": List[str]}
    """
    # BOM 제거 및 UTF-8 디코딩
    if file_content.startswith(b'\xef\xbb\xbf'):
        file_content = file_content[3:]
    
    try:
        text = file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = file_content.decode('cp949')  # 한글 Windows 인코딩
        except UnicodeDecodeError:
            text = file_content.decode('latin-1')  # fallback
    
    reader = csv.reader(StringIO(text))
    
    success_count = 0
    failed_count = 0
    errors = []
    
    # 헤더 행 건너뛰기
    next(reader, None)
    
    for row_idx, row in enumerate(reader, start=2):
        try:
            # 빈 행 건너뛰기
            if not row or not row[0]:
                continue
            
            # 데이터 파싱
            transaction_date = datetime.strptime(row[0].strip(), "%Y-%m-%d").date()
            
            type_str = row[1].strip()
            if type_str not in ["수입", "지출", "income", "expense"]:
                raise ValueError(f"유형이 올바르지 않습니다: {type_str}")
            transaction_type = "income" if type_str in ["수입", "income"] else "expense"
            
            category_name = row[2].strip()
            if not category_name:
                raise ValueError("카테고리명이 비어있습니다")
            
            # 카테고리 찾기 또는 생성
            if category_name not in categories:
                category = Category(
                    name=category_name,
                    type=transaction_type,
                    user_id=user_id,
                    color="#6b7280"
                )
                db.add(category)
                db.flush()
                categories[category_name] = category
            else:
                category = categories[category_name]
                if category.type != transaction_type:
                    raise ValueError(
                        f"카테고리 '{category_name}'의 타입({category.type})이 거래 유형({transaction_type})과 일치하지 않습니다"
                    )
            
            amount = float(row[3])
            if amount < 0:
                raise ValueError(f"금액은 0원 이상이어야 합니다: {amount}")
            
            description = row[4].strip() if len(row) > 4 and row[4] else None
            
            # 거래 내역 생성
            transaction = Transaction(
                user_id=user_id,
                category_id=category.id,
                type=transaction_type,
                amount=Decimal(str(amount)),
                description=description,
                transaction_date=transaction_date
            )
            db.add(transaction)
            success_count += 1
            
        except Exception as e:
            failed_count += 1
            error_msg = f"행 {row_idx}: {str(e)}"
            errors.append(error_msg)
            continue
    
    # 변경사항 저장
    if success_count > 0:
        db.commit()
    
    return {
        "success": success_count,
        "failed": failed_count,
        "errors": errors
    }


def export_categories_to_csv(
    db: Session,
    categories: List[Category]
) -> BytesIO:
    """
    카테고리를 CSV 파일로 변환
    
    Args:
        db: 데이터베이스 세션
        categories: 카테고리 리스트
    
    Returns:
        BytesIO: CSV 파일 바이트 스트림 (UTF-8 with BOM for Excel compatibility)
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # BOM 추가 (Excel에서 UTF-8 인식)
    output.write('\ufeff')
    
    # 헤더 작성
    headers = ["이름", "유형", "색상", "아이콘", "등록일시", "수정일시"]
    writer.writerow(headers)
    
    # 데이터 작성
    for category in categories:
        created_at = category.created_at
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        elif not isinstance(created_at, datetime):
            created_at = datetime.now()
        
        updated_at = category.updated_at
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        elif not isinstance(updated_at, datetime):
            updated_at = datetime.now()
        
        row = [
            category.name,
            "수입" if category.type == "income" else "지출",
            category.color or "",
            category.icon or "",
            created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        ]
        writer.writerow(row)
    
    # StringIO를 BytesIO로 변환
    output.seek(0)
    csv_bytes = BytesIO(output.getvalue().encode('utf-8-sig'))  # UTF-8 with BOM
    csv_bytes.seek(0)
    
    return csv_bytes


def import_categories_from_csv(
    db: Session,
    file_content: bytes,
    user_id: int
) -> Dict[str, Any]:
    """
    CSV 파일에서 카테고리를 읽어서 데이터베이스에 저장
    
    Args:
        db: 데이터베이스 세션
        file_content: CSV 파일 바이트
        user_id: 사용자 ID
    
    Returns:
        Dict: {"success": int, "failed": int, "errors": List[str]}
    """
    # BOM 제거 및 UTF-8 디코딩
    if file_content.startswith(b'\xef\xbb\xbf'):
        file_content = file_content[3:]
    
    try:
        text = file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = file_content.decode('cp949')  # 한글 Windows 인코딩
        except UnicodeDecodeError:
            text = file_content.decode('latin-1')  # fallback
    
    reader = csv.reader(StringIO(text))
    
    success_count = 0
    failed_count = 0
    errors = []
    
    # 헤더 행 건너뛰기
    next(reader, None)
    
    for row_idx, row in enumerate(reader, start=2):
        try:
            # 빈 행 건너뛰기
            if not row or not row[0]:
                continue
            
            # 데이터 파싱
            name = row[0].strip()
            if not name:
                raise ValueError("카테고리 이름이 비어있습니다")
            
            type_str = row[1].strip()
            if type_str not in ["수입", "지출", "income", "expense"]:
                raise ValueError(f"유형이 올바르지 않습니다: {type_str}")
            category_type = "income" if type_str in ["수입", "income"] else "expense"
            
            color = row[2].strip() if len(row) > 2 and row[2] else None
            if color and not color.startswith("#"):
                if len(color) == 6:
                    color = "#" + color
                else:
                    color = None
            
            icon = row[3].strip() if len(row) > 3 and row[3] else None
            
            # 기존 카테고리 확인
            existing = db.query(Category).filter(
                Category.name == name,
                Category.type == category_type,
                Category.user_id == user_id
            ).first()
            
            if existing:
                # 기존 카테고리 업데이트
                if color:
                    existing.color = color
                if icon:
                    existing.icon = icon
                success_count += 1
            else:
                # 새 카테고리 생성
                category = Category(
                    name=name,
                    type=category_type,
                    user_id=user_id,
                    color=color or "#6b7280",
                    icon=icon
                )
                db.add(category)
                success_count += 1
            
        except Exception as e:
            failed_count += 1
            error_msg = f"행 {row_idx}: {str(e)}"
            errors.append(error_msg)
            continue
    
    # 변경사항 저장
    if success_count > 0:
        db.commit()
    
    return {
        "success": success_count,
        "failed": failed_count,
        "errors": errors
    }
