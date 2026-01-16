import httpx
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# 백엔드 API 기본 URL
API_BASE_URL = "http://localhost:8000"

# #region agent log
import os
LOG_DIR = r"c:\dev\git\ncaco97\2026\2026_idea_mvp_01\.cursor"
LOG_PATH = os.path.join(LOG_DIR, "debug.log")
def _log(session_id, run_id, hypothesis_id, location, message, data):
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({"sessionId": session_id, "runId": run_id, "hypothesisId": hypothesis_id, "location": location, "message": message, "data": data, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
            f.flush()
    except Exception as e:
        print(f"로그 쓰기 실패: {e}, 경로: {LOG_PATH}")
# #endregion

def get_transactions(
    limit: int = 50,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """거래 내역을 조회합니다."""
    # #region agent log
    _log("debug-session", "run1", "A", "api_client.py:get_transactions", "함수 진입", {"limit": limit, "start_date": start_date, "end_date": end_date, "api_url": f"{API_BASE_URL}/api/transactions"})
    # #endregion
    try:
        params = {"limit": limit}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        # #region agent log
        _log("debug-session", "run1", "A", "api_client.py:get_transactions", "API 요청 전", {"params": params})
        # #endregion
        
        response = httpx.get(
            f"{API_BASE_URL}/api/transactions",
            params=params,
            timeout=10.0
        )
        
        # #region agent log
        _log("debug-session", "run1", "A", "api_client.py:get_transactions", "API 응답 수신", {"status_code": response.status_code})
        # #endregion
        
        response.raise_for_status()
        result = response.json()
        
        # #region agent log
        _log("debug-session", "run1", "A", "api_client.py:get_transactions", "함수 종료", {"result_count": len(result) if isinstance(result, list) else 0})
        # #endregion
        
        return result
    except Exception as e:
        # #region agent log
        _log("debug-session", "run1", "A", "api_client.py:get_transactions", "오류 발생", {"error": str(e), "error_type": type(e).__name__})
        # #endregion
        print(f"거래 내역 조회 실패: {e}")
        return []

def get_monthly_statistics(
    year: Optional[int] = None,
    month: Optional[int] = None
) -> Dict:
    """월별 통계를 조회합니다."""
    try:
        params = {}
        if year:
            params["year"] = year
        if month:
            params["month"] = month
        
        response = httpx.get(
            f"{API_BASE_URL}/api/statistics/monthly",
            params=params,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"월별 통계 조회 실패: {e}")
        return {"income": 0, "expense": 0, "balance": 0}

def get_category_statistics(
    year: Optional[int] = None,
    month: Optional[int] = None,
    type: str = "expense"
) -> List[Dict]:
    """카테고리별 통계를 조회합니다."""
    try:
        params = {"type": type}
        if year:
            params["year"] = year
        if month:
            params["month"] = month
        
        response = httpx.get(
            f"{API_BASE_URL}/api/statistics/by-category",
            params=params,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"카테고리별 통계 조회 실패: {e}")
        return []

def get_categories() -> List[Dict]:
    """카테고리 목록을 조회합니다."""
    try:
        response = httpx.get(
            f"{API_BASE_URL}/api/categories",
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"카테고리 조회 실패: {e}")
        return []

def get_accountbook_context(user_question: Optional[str] = None) -> str:
    """
    가계부 데이터를 수집하여 컨텍스트 문자열로 반환합니다.
    
    Args:
        user_question: 사용자 질문 (날짜 정보 추출용)
    """
    # #region agent log
    _log("debug-session", "run1", "B", "api_client.py:get_accountbook_context", "함수 진입", {"user_question": user_question[:100] if user_question else None})
    # #endregion
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # 질문에서 날짜 정보 추출
    from date_extractor import extract_date_from_question, extract_comparison_dates
    
    target_dates = []
    
    # 비교 질문인지 확인
    comparison_dates = extract_comparison_dates(user_question) if user_question else None
    if comparison_dates:
        target_dates.extend([comparison_dates[0], comparison_dates[1]])
    else:
        # 단일 날짜 추출
        extracted_date = extract_date_from_question(user_question) if user_question else None
        if extracted_date:
            target_dates.append(extracted_date)
    
    # 현재 년도/월도 항상 포함
    target_dates.append((current_year, current_month))
    
    # 중복 제거
    target_dates = list(set(target_dates))
    
    # #region agent log
    _log("debug-session", "run1", "B", "api_client.py:get_accountbook_context", "추출된 날짜", {"target_dates": target_dates})
    # #endregion
    
    # 최근 거래 내역 (최근 1년으로 확장)
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - timedelta(days=365)).strftime("%Y-%m-%d")
    
    # #region agent log
    _log("debug-session", "run1", "B", "api_client.py:get_accountbook_context", "거래 내역 조회 전", {"start_date": start_date, "end_date": end_date})
    # #endregion
    
    recent_transactions = get_transactions(limit=100, start_date=start_date, end_date=end_date)
    
    # #region agent log
    _log("debug-session", "run1", "B", "api_client.py:get_accountbook_context", "거래 내역 조회 후", {"transaction_count": len(recent_transactions)})
    # #endregion
    
    # 각 대상 년도/월의 통계 수집
    all_monthly_stats = {}
    all_category_stats = {}
    
    for year, month in target_dates:
        if month is None:
            # 월이 없으면 해당 년도의 모든 월 데이터 수집
            for m in range(1, 13):
                stats = get_monthly_statistics(year, m)
                if stats.get('income', 0) or stats.get('expense', 0):
                    all_monthly_stats[(year, m)] = stats
                    
                    # 카테고리별 통계도 수집 (수입, 지출 모두)
                    income_cat_stats = get_category_statistics(year, m, "income")
                    expense_cat_stats = get_category_statistics(year, m, "expense")
                    if income_cat_stats or expense_cat_stats:
                        all_category_stats[(year, m)] = {
                            "income": income_cat_stats,
                            "expense": expense_cat_stats
                        }
        else:
            stats = get_monthly_statistics(year, month)
            all_monthly_stats[(year, month)] = stats
            
            # 카테고리별 통계도 수집 (수입, 지출 모두)
            income_cat_stats = get_category_statistics(year, month, "income")
            expense_cat_stats = get_category_statistics(year, month, "expense")
            if income_cat_stats or expense_cat_stats:
                all_category_stats[(year, month)] = {
                    "income": income_cat_stats,
                    "expense": expense_cat_stats
                }
    
    # #region agent log
    _log("debug-session", "run1", "B", "api_client.py:get_accountbook_context", "월별 통계 조회 후", {"stats_count": len(all_monthly_stats)})
    # #endregion
    
    # 카테고리 목록
    categories = get_categories()
    
    # #region agent log
    _log("debug-session", "run1", "B", "api_client.py:get_accountbook_context", "카테고리 조회 후", {"category_count": len(categories)})
    # #endregion
    
    # 컨텍스트 포맷팅
    context_parts = []
    
    # 각 년도/월별 통계
    for (year, month), stats in sorted(all_monthly_stats.items()):
        context_parts.append(f"=== {year}년 {month}월 통계 ===")
        income = float(stats.get('income', 0) or 0)
        expense = float(stats.get('expense', 0) or 0)
        balance = float(stats.get('balance', 0) or 0)
        context_parts.append(f"총 수입: {income:,.0f}원")
        context_parts.append(f"총 지출: {expense:,.0f}원")
        context_parts.append(f"잔액: {balance:,.0f}원")
        context_parts.append("")
        
        # 해당 월의 카테고리별 통계 (수입, 지출)
        if (year, month) in all_category_stats:
            cat_stats_dict = all_category_stats[(year, month)]
            
            # 수입 카테고리
            if cat_stats_dict.get("income"):
                context_parts.append(f"=== {year}년 {month}월 카테고리별 수입 ===")
                for cat in cat_stats_dict["income"][:10]:  # 상위 10개만
                    total = float(cat.get('total', 0) or 0)
                    count = int(cat.get('count', 0) or 0)
                    context_parts.append(
                        f"- {cat.get('category_name', '알 수 없음')}: "
                        f"{total:,.0f}원 ({count}건)"
                    )
                context_parts.append("")
            
            # 지출 카테고리
            if cat_stats_dict.get("expense"):
                context_parts.append(f"=== {year}년 {month}월 카테고리별 지출 ===")
                for cat in cat_stats_dict["expense"][:10]:  # 상위 10개만
                    total = float(cat.get('total', 0) or 0)
                    count = int(cat.get('count', 0) or 0)
                    context_parts.append(
                        f"- {cat.get('category_name', '알 수 없음')}: "
                        f"{total:,.0f}원 ({count}건)"
                    )
                context_parts.append("")
    
    # 카테고리 ID -> 이름 매핑 생성
    category_map = {cat.get('id'): cat.get('name', '') for cat in categories}
    
    # 최근 거래 내역 (최근 1년)
    if recent_transactions:
        # 질문에서 언급된 년도/월의 거래 필터링
        filtered_transactions = []
        for trans in recent_transactions:
            trans_date_str = trans.get('transaction_date', '')
            if trans_date_str:
                try:
                    trans_date = datetime.strptime(trans_date_str, '%Y-%m-%d').date()
                    trans_year = trans_date.year
                    trans_month = trans_date.month
                    # 대상 날짜 중 하나와 일치하는지 확인
                    matches = any((trans_year == y and (m is None or trans_month == m)) for y, m in target_dates)
                    if matches:
                        filtered_transactions.append(trans)
                except:
                    pass
        
        # 필터링 결과가 없거나 너무 적으면, 최근 거래도 포함 (최대 50건)
        if len(filtered_transactions) < 10:
            # 필터링된 거래 + 최근 거래 병합
            all_relevant = filtered_transactions + [t for t in recent_transactions[:50] if t not in filtered_transactions]
            filtered_transactions = all_relevant[:50]
        
        # 대상 날짜별로 그룹화하여 표시
        transactions_by_date = {}
        for trans in filtered_transactions:
            trans_date_str = trans.get('transaction_date', '')
            if trans_date_str:
                try:
                    trans_date = datetime.strptime(trans_date_str, '%Y-%m-%d').date()
                    key = (trans_date.year, trans_date.month)
                    if key not in transactions_by_date:
                        transactions_by_date[key] = []
                    transactions_by_date[key].append(trans)
                except:
                    pass
        
        # 각 년도/월별로 거래 내역 표시
        for (year, month) in sorted(transactions_by_date.keys(), reverse=True):
            month_transactions = transactions_by_date[(year, month)]
            context_parts.append(f"=== {year}년 {month}월 거래 내역 ({len(month_transactions)}건) ===")
            for trans in month_transactions[:20]:  # 월별 최대 20건
                trans_date = trans.get('transaction_date', '')
                trans_type = "수입" if trans.get('type') == 'income' else "지출"
                amount = float(trans.get('amount', 0) or 0)
                description = trans.get('description', '')
                category_id = trans.get('category_id')
                category_name = category_map.get(category_id, '')
                
                context_parts.append(
                    f"- {trans_date}: {trans_type} {amount:,.0f}원"
                    + (f" [{category_name}]" if category_name else "")
                    + (f" ({description})" if description else "")
                )
            context_parts.append("")
    
    # 카테고리 목록
    if categories:
        income_cats = [c for c in categories if c.get('type') == 'income']
        expense_cats = [c for c in categories if c.get('type') == 'expense']
        
        context_parts.append("=== 카테고리 목록 ===")
        if income_cats:
            context_parts.append("수입 카테고리: " + ", ".join([c.get('name', '') for c in income_cats]))
        if expense_cats:
            context_parts.append("지출 카테고리: " + ", ".join([c.get('name', '') for c in expense_cats]))
        context_parts.append("")
    
    context_str = "\n".join(context_parts)
    
    # #region agent log
    _log("debug-session", "run1", "B", "api_client.py:get_accountbook_context", "함수 종료", {"context_length": len(context_str)})
    # #endregion
    
    return context_str
