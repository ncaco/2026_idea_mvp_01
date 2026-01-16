from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.schemas.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.services import transaction_service
from app.services.excel_service import export_transactions_to_excel, import_transactions_from_excel
from app.core.security import get_current_user
from app.models import User, Category

router = APIRouter()


@router.post("", response_model=Transaction, status_code=201)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """거래 내역 생성"""
    return transaction_service.create_transaction(db, transaction, current_user.id)


@router.get("", response_model=List[Transaction])
def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None, regex="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """거래 내역 목록 조회"""
    return transaction_service.get_transactions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        transaction_type=type
    )


@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """거래 내역 상세 조회"""
    transaction = transaction_service.get_transaction(db, transaction_id, current_user.id)
    if not transaction:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    return transaction


@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """거래 내역 수정"""
    transaction = transaction_service.update_transaction(
        db, transaction_id, current_user.id, transaction_update
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    return transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """거래 내역 삭제"""
    success = transaction_service.delete_transaction(db, transaction_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    return None


@router.get("/export/excel")
def export_transactions(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None, regex="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """거래 내역을 엑셀 파일로 다운로드"""
    # 거래 내역 조회
    transactions = transaction_service.get_transactions(
        db=db,
        user_id=current_user.id,
        skip=0,
        limit=10000,  # 최대 10000건까지
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        transaction_type=type
    )
    
    if not transactions:
        raise HTTPException(status_code=404, detail="다운로드할 거래 내역이 없습니다")
    
    # 카테고리 정보 조회
    category_ids = {t.category_id for t in transactions}
    categories = db.query(Category).filter(
        Category.id.in_(category_ids),
        Category.user_id == current_user.id
    ).all()
    categories_dict = {c.id: c for c in categories}
    
    # 엑셀 파일 생성
    excel_file = export_transactions_to_excel(db, transactions, categories_dict)
    
    # 파일명 생성
    from datetime import datetime
    from urllib.parse import quote
    filename = f"거래내역_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filename_encoded = quote(filename, safe='')
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"
        }
    )


@router.post("/import/excel")
async def import_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """엑셀 파일에서 거래 내역을 일괄 등록"""
    # 파일 확장자 확인
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일(.xlsx, .xls)만 업로드 가능합니다")
    
    # 파일 읽기
    file_content = await file.read()
    
    # 카테고리 정보 조회 (카테고리명으로 매핑)
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    categories_dict = {c.name: c for c in categories}
    
    # 엑셀 파일 파싱 및 저장
    result = import_transactions_from_excel(
        db=db,
        file_content=file_content,
        user_id=current_user.id,
        categories=categories_dict
    )
    
    return {
        "message": "엑셀 파일 업로드가 완료되었습니다",
        "success": result["success"],
        "failed": result["failed"],
        "errors": result["errors"][:10]  # 최대 10개 오류만 반환
    }


@router.delete("", status_code=200)
def delete_all_transactions(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None, regex="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """거래 내역 전체 삭제 (필터 조건 적용 가능)"""
    deleted_count = transaction_service.delete_all_transactions(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        transaction_type=type
    )
    return {"message": f"{deleted_count}건의 거래 내역이 삭제되었습니다", "deleted_count": deleted_count}
