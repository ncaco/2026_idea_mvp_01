"""
AI 기능 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.services import ai_service

router = APIRouter()


class CategoryClassificationRequest(BaseModel):
    description: str
    transaction_type: str = "expense"


class CategoryClassificationResponse(BaseModel):
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    confidence: float = 0.0


class NaturalLanguageParseRequest(BaseModel):
    text: str


class NaturalLanguageParseResponse(BaseModel):
    transaction_date: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    description: str
    type: str = "expense"


@router.post("/classify-category", response_model=CategoryClassificationResponse)
def classify_category(
    request: CategoryClassificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """거래 설명을 기반으로 카테고리 자동 분류"""
    if request.transaction_type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="transaction_type은 'income' 또는 'expense'여야 합니다")
    
    result = ai_service.classify_category_by_description(
        db=db,
        description=request.description,
        user_id=current_user.id,
        transaction_type=request.transaction_type
    )
    
    if result:
        return CategoryClassificationResponse(
            **result,
            description=request.description
        )
    else:
        return CategoryClassificationResponse(
            description=request.description,
            confidence=0.0
        )


@router.post("/parse-natural-language", response_model=NaturalLanguageParseResponse)
def parse_natural_language(
    request: NaturalLanguageParseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """자연어 텍스트에서 거래 정보 추출"""
    result = ai_service.parse_natural_language(
        text=request.text,
        user_id=current_user.id,
        db=db
    )
    
    # 날짜를 문자열로 변환
    if result.get("transaction_date"):
        result["transaction_date"] = result["transaction_date"].isoformat()
    
    return NaturalLanguageParseResponse(**result)


@router.get("/spending-patterns")
def get_spending_patterns(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """지출 패턴 분석"""
    start = None
    end = None
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date 형식이 올바르지 않습니다 (ISO 형식 사용)")
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="end_date 형식이 올바르지 않습니다 (ISO 형식 사용)")
    
    result = ai_service.analyze_spending_patterns(
        db=db,
        user_id=current_user.id,
        start_date=start,
        end_date=end
    )
    
    return result
