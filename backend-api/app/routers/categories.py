from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from urllib.parse import quote
from datetime import datetime
from app.database import get_db
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.services import category_service
from app.services.excel_service import export_categories_to_excel, import_categories_from_excel
from app.core.security import get_current_user
from app.models import User

router = APIRouter()


@router.get("", response_model=List[Category])
def get_categories(
    type: Optional[str] = Query(None, regex="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 목록 조회"""
    return category_service.get_categories(
        db=db,
        user_id=current_user.id,
        category_type=type
    )


@router.post("", response_model=Category, status_code=201)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 생성"""
    return category_service.create_category(db, category, current_user.id)


@router.get("/{category_id}", response_model=Category)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 상세 조회"""
    category = category_service.get_category(db, category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return category


@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 수정"""
    category = category_service.update_category(
        db, category_id, current_user.id, category_update
    )
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 삭제"""
    success = category_service.delete_category(db, category_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return None


@router.get("/export/excel")
def export_categories(
    type: Optional[str] = Query(None, regex="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리를 엑셀 파일로 다운로드"""
    # 카테고리 조회
    categories = category_service.get_categories(
        db=db,
        user_id=current_user.id,
        category_type=type
    )
    
    if not categories:
        raise HTTPException(status_code=404, detail="다운로드할 카테고리가 없습니다")
    
    # 엑셀 파일 생성
    excel_file = export_categories_to_excel(db, categories)
    
    # 파일명 생성
    filename = f"카테고리_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filename_encoded = quote(filename, safe='')
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"
        }
    )


@router.post("/import/excel")
async def import_categories(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """엑셀 파일에서 카테고리를 일괄 등록"""
    # 파일 확장자 확인
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일(.xlsx, .xls)만 업로드 가능합니다")
    
    # 파일 읽기
    file_content = await file.read()
    
    # 엑셀 파일 파싱 및 저장
    result = import_categories_from_excel(
        db=db,
        file_content=file_content,
        user_id=current_user.id
    )
    
    return {
        "message": "엑셀 파일 업로드가 완료되었습니다",
        "success": result["success"],
        "failed": result["failed"],
        "errors": result["errors"][:10]  # 최대 10개 오류만 반환
    }


@router.delete("", status_code=200)
def delete_all_categories(
    type: Optional[str] = Query(None, regex="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 전체 삭제 (타입별 필터 적용 가능)"""
    deleted_count = category_service.delete_all_categories(
        db=db,
        user_id=current_user.id,
        category_type=type
    )
    return {"message": f"{deleted_count}개의 카테고리가 삭제되었습니다", "deleted_count": deleted_count}
