"""
LangChain 도구 정의
가계부 데이터 조회를 위한 도구들
"""
import json
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from api_client import (
    get_transactions,
    get_monthly_statistics,
    get_category_statistics,
    get_categories,
    search_transactions
)


@tool
def get_transactions_tool(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    limit: int = 100
) -> str:
    """
    엘라스틱서치를 사용한 하이브리드 검색으로 거래 내역을 조회합니다.
    키워드 검색과 의미 기반 검색을 결합하여 더 정확한 결과를 제공합니다.
    
    Args:
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        category_id: 카테고리 ID (선택)
        transaction_type: 거래 타입 ("income" 또는 "expense")
        keywords: 검색할 키워드 리스트 (예: ["남편", "월급"])
                  키워드가 있으면 엘라스틱서치 하이브리드 검색 사용
        limit: 최대 조회 개수 (기본값: 100)
    
    Returns:
        JSON 문자열로 변환된 거래 내역 리스트
    """
    try:
        # 키워드가 있으면 엘라스틱서치 하이브리드 검색 사용
        if keywords:
            # 키워드를 자연어 질문으로 변환
            query_text = " ".join(keywords)
            
            # 엘라스틱서치 검색
            transactions = search_transactions(
                query=query_text,
                start_date=start_date,
                end_date=end_date,
                transaction_type=transaction_type,
                category_id=category_id,
                size=limit
            )
            
            # 검색 결과가 없으면 키워드 없이 일반 조회로 폴백
            if not transactions:
                transactions = get_transactions(
                    limit=limit,
                    start_date=start_date,
                    end_date=end_date
                )
                
                # 필터링
                filtered = []
                for trans in transactions:
                    if category_id and trans.get('category_id') != category_id:
                        continue
                    if transaction_type and trans.get('type') != transaction_type:
                        continue
                    filtered.append(trans)
                transactions = filtered[:limit]
        else:
            # 키워드가 없으면 일반 조회
            transactions = get_transactions(
                limit=limit,
                start_date=start_date,
                end_date=end_date
            )
            
            # 필터링
            filtered = []
            for trans in transactions:
                if category_id and trans.get('category_id') != category_id:
                    continue
                if transaction_type and trans.get('type') != transaction_type:
                    continue
                filtered.append(trans)
            transactions = filtered[:limit]
        
        return json.dumps(transactions, ensure_ascii=False, default=str)
    except Exception as e:
        # 엘라스틱서치 검색 실패 시 일반 조회로 폴백
        try:
            transactions = get_transactions(
                limit=limit,
                start_date=start_date,
                end_date=end_date
            )
            
            # 필터링
            filtered = []
            for trans in transactions:
                if category_id and trans.get('category_id') != category_id:
                    continue
                if transaction_type and trans.get('type') != transaction_type:
                    continue
                if keywords:
                    description = trans.get('description', '').lower() if trans.get('description') else ''
                    matches = any(
                        keyword.lower() in description
                        for keyword in keywords
                        if keyword
                    )
                    if not matches:
                        continue
                filtered.append(trans)
            
            transactions = filtered[:limit]
            return json.dumps(transactions, ensure_ascii=False, default=str)
        except Exception as fallback_error:
            return json.dumps({"error": f"검색 실패: {str(e)}, 폴백 실패: {str(fallback_error)}"})


@tool
def get_monthly_statistics_tool(
    year: Optional[int] = None,
    month: Optional[int] = None
) -> str:
    """
    월별 수입/지출 통계를 조회합니다.
    
    Args:
        year: 년도 (예: 2025)
        month: 월 (1-12)
    
    Returns:
        JSON 문자열로 변환된 통계 데이터
        {"income": 0, "expense": 0, "balance": 0, "year": 2025, "month": 1}
    """
    try:
        stats = get_monthly_statistics(year=year, month=month)
        return json.dumps(stats, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_category_statistics_tool(
    year: Optional[int] = None,
    month: Optional[int] = None,
    category_type: str = "expense"
) -> str:
    """
    카테고리별 통계를 조회합니다.
    
    Args:
        year: 년도 (예: 2025)
        month: 월 (1-12)
        category_type: "income" 또는 "expense" (기본값: "expense")
    
    Returns:
        JSON 문자열로 변환된 카테고리별 통계 리스트
        [{"category_id": 1, "category_name": "식비", "total": 100000, "count": 5}, ...]
    """
    try:
        stats = get_category_statistics(year=year, month=month, type=category_type)
        return json.dumps(stats, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_categories_tool() -> str:
    """
    카테고리 목록을 조회합니다.
    
    Returns:
        JSON 문자열로 변환된 카테고리 리스트
        [{"id": 1, "name": "식비", "type": "expense", "color": "#FF0000"}, ...]
    """
    try:
        categories = get_categories()
        return json.dumps(categories, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


# 도구 목록
AVAILABLE_TOOLS = [
    get_transactions_tool,
    get_monthly_statistics_tool,
    get_category_statistics_tool,
    get_categories_tool
]

# 도구 이름 매핑
TOOL_MAP = {
    "get_transactions": get_transactions_tool,
    "get_monthly_statistics": get_monthly_statistics_tool,
    "get_category_statistics": get_category_statistics_tool,
    "get_categories": get_categories_tool
}
