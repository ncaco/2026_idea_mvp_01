"""
엘라스틱서치 서비스
거래 내역 인덱싱 및 검색 로직
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models import Transaction, Category
from app.core.elasticsearch import (
    get_elasticsearch_client,
    index_document,
    update_document,
    delete_document,
    hybrid_search,
    create_index_if_not_exists
)
from app.services.embedding_service import generate_embedding, generate_embeddings_batch
import logging

logger = logging.getLogger(__name__)


def prepare_document_for_indexing(
    transaction: Transaction,
    category: Optional[Category] = None
) -> Dict[str, Any]:
    """
    거래 내역을 엘라스틱서치 문서 형식으로 변환
    
    Args:
        transaction: 거래 내역 모델
        category: 카테고리 모델 (선택)
    
    Returns:
        엘라스틱서치 문서 딕셔너리
    """
    # description과 카테고리명을 결합하여 검색 텍스트 생성
    search_text_parts = []
    if transaction.description:
        search_text_parts.append(transaction.description)
    if category:
        search_text_parts.append(category.name)
    
    search_text = " ".join(search_text_parts)
    
    # 벡터 임베딩 생성 (모델이 로드되지 않으면 None)
    embedding = generate_embedding(search_text) if search_text.strip() else None
    
    # 날짜 형식 변환
    transaction_date_str = transaction.transaction_date.isoformat() if isinstance(transaction.transaction_date, date) else str(transaction.transaction_date)
    created_at_str = transaction.created_at.isoformat() if transaction.created_at else None
    updated_at_str = transaction.updated_at.isoformat() if transaction.updated_at else None
    
    document = {
        "transaction_id": transaction.id,
        "user_id": transaction.user_id,
        "category_id": transaction.category_id,
        "category_name": category.name if category else "",
        "category_color": category.color if category else None,
        "type": transaction.type,
        "amount": float(transaction.amount),
        "description": transaction.description or "",
        "description_text": search_text,
        "transaction_date": transaction_date_str,
        "created_at": created_at_str,
        "updated_at": updated_at_str
    }
    
    # 임베딩이 있으면 추가 (없으면 제외하여 제로 벡터 오류 방지)
    if embedding is not None:
        document["description_embedding"] = embedding
    
    return document


def index_transaction(
    db: Session,
    transaction: Transaction,
    category: Optional[Category] = None
) -> bool:
    """
    거래 내역을 엘라스틱서치에 인덱싱
    
    Args:
        db: 데이터베이스 세션
        transaction: 거래 내역 모델
        category: 카테고리 모델 (없으면 조회)
    
    Returns:
        인덱싱 성공 여부
    """
    try:
        # 인덱스가 없으면 생성
        create_index_if_not_exists()
        
        # 카테고리 정보가 없으면 조회
        if not category:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
        
        # 문서 준비
        document = prepare_document_for_indexing(transaction, category)
        
        # 인덱싱
        return index_document(document)
    except Exception as e:
        logger.error(f"거래 내역 인덱싱 실패 (transaction_id={transaction.id}): {e}")
        return False


def update_transaction_index(
    db: Session,
    transaction: Transaction,
    category: Optional[Category] = None
) -> bool:
    """
    거래 내역 인덱스 업데이트
    
    Args:
        db: 데이터베이스 세션
        transaction: 거래 내역 모델
        category: 카테고리 모델 (없으면 조회)
    
    Returns:
        업데이트 성공 여부
    """
    try:
        # 카테고리 정보가 없으면 조회
        if not category:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
        
        # 문서 준비
        document = prepare_document_for_indexing(transaction, category)
        
        # 업데이트
        return update_document(transaction.id, document)
    except Exception as e:
        logger.error(f"거래 내역 인덱스 업데이트 실패 (transaction_id={transaction.id}): {e}")
        return False


def delete_transaction_index(transaction_id: int) -> bool:
    """
    거래 내역 인덱스에서 삭제
    
    Args:
        transaction_id: 거래 내역 ID
    
    Returns:
        삭제 성공 여부
    """
    try:
        return delete_document(transaction_id)
    except Exception as e:
        logger.error(f"거래 내역 인덱스 삭제 실패 (transaction_id={transaction_id}): {e}")
        return False


def search_transactions(
    query_text: str,
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
    category_id: Optional[int] = None,
    size: int = 20
) -> List[Dict[str, Any]]:
    """
    하이브리드 검색으로 거래 내역 검색
    
    Args:
        query_text: 검색 키워드
        user_id: 사용자 ID
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
        transaction_type: 거래 타입 ("income" or "expense")
        category_id: 카테고리 ID
        size: 반환할 결과 수
    
    Returns:
        거래 내역 리스트
    """
    try:
        # 검색어 벡터 임베딩 생성 (모델이 로드되지 않으면 None)
        query_embedding = generate_embedding(query_text)
        
        # 하이브리드 검색 수행 (임베딩이 없으면 BM25만 사용)
        search_result = hybrid_search(
            query_text=query_text,
            query_embedding=query_embedding,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            category_id=category_id,
            size=size
        )
        
        # 결과 변환
        transactions = []
        for hit in search_result.get("hits", {}).get("hits", []):
            source = hit["_source"]
            transactions.append({
                "id": source["transaction_id"],
                "user_id": source["user_id"],
                "category_id": source["category_id"],
                "category_name": source.get("category_name", ""),
                "category_color": source.get("category_color"),
                "type": source["type"],
                "amount": source["amount"],
                "description": source.get("description", ""),
                "transaction_date": source["transaction_date"],
                "created_at": source.get("created_at"),
                "updated_at": source.get("updated_at"),
                "_score": hit.get("_score", 0)  # 검색 점수 포함
            })
        
        return transactions
    except Exception as e:
        logger.error(f"거래 내역 검색 실패: {e}")
        return []
