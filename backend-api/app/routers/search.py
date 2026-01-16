"""
검색 API 엔드포인트
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.services.elasticsearch_service import search_transactions
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/transactions")
def search_transactions_endpoint(
    q: str = Query(..., description="검색 키워드"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    type: Optional[str] = Query(None, regex="^(income|expense)$", description="거래 타입"),
    category_id: Optional[int] = Query(None, description="카테고리 ID"),
    size: int = Query(20, ge=1, le=100, description="반환할 결과 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    엘라스틱서치를 사용한 하이브리드 검색
    
    키워드 검색(BM25)과 의미 기반 검색(kNN)을 결합하여
    거래 내역을 검색합니다.
    """
    try:
        results = search_transactions(
            query_text=q,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=type,
            category_id=category_id,
            size=size
        )
        
        return {
            "query": q,
            "total": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"검색 오류: {e}")
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")
