"""
LangGraph 기반 동적 데이터 조회 Agent
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from state import AgentState
from tools import AVAILABLE_TOOLS, TOOL_MAP
from date_extractor import extract_date_from_question, extract_comparison_dates


def create_llm(lmstudio_url: str, model: str = ""):
    """LM Studio를 위한 ChatOpenAI 인스턴스 생성"""
    return ChatOpenAI(
        base_url=f"{lmstudio_url}/v1",
        api_key="not-needed",  # LM Studio는 API 키가 필요 없음
        model=model or "local-model",
        temperature=0.7,
        timeout=300.0
    )


def analyze_question(state: AgentState, llm: Any = None) -> AgentState:
    """질문을 분석하여 필요한 데이터 타입과 파라미터를 결정"""
    question = state["question"]
    
    # llm이 매개변수로 전달되지 않으면 state에서 가져오기 시도
    if llm is None:
        llm = state.get("llm")
    
    if not llm:
        state["error"] = "LLM이 초기화되지 않았습니다."
        return state
    
    # 날짜 정보 추출 (기존 로직 활용)
    extracted_date = extract_date_from_question(question)
    comparison_dates = extract_comparison_dates(question)
    
    # 현재 년도 정보
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # 질문 분석 프롬프트
    analysis_prompt = f"""사용자의 질문을 분석하여 필요한 데이터를 파악하세요.

중요: 현재 년도 정보
- 현재 년도: {current_year}년 {current_month}월
- '재작년'은 {current_year - 2}년을 의미합니다
- '재작년 1월'은 {current_year - 2}년 1월을 의미합니다
- '작년'은 {current_year - 1}년을 의미합니다
- '작년 1월'은 {current_year - 1}년 1월을 의미합니다
- '올해' 또는 '이번'은 {current_year}년을 의미합니다

사용자 질문: {question}

다음 정보를 JSON 형식으로 반환하세요:
{{
    "data_types": ["transactions", "monthly_statistics", "category_statistics", "categories"],
    "date_info": {{
        "year": null,
        "month": null,
        "start_date": null,
        "end_date": null
    }},
    "filters": {{
        "category_type": null,
        "transaction_type": null,
        "category_id": null,
        "keywords": []
    }},
    "reasoning": "왜 이 데이터가 필요한지 간단히 설명"
}}

사용 가능한 데이터 타입:
- transactions: 거래 내역
- monthly_statistics: 월별 통계
- category_statistics: 카테고리별 통계
- categories: 카테고리 목록

filters.keywords는 질문에서 언급된 중요한 키워드들을 배열로 추출하세요.
키워드가 있으면 엘라스틱서치 하이브리드 검색(키워드 + 의미 기반)을 사용하여 더 정확한 결과를 얻을 수 있습니다.
예: "작년 1월 남편 월급" → ["남편", "월급"]
예: "식비 지출" → ["식비"]
예: "토익학원 비용" → ["토익", "학원"]
예: "배우자 급여" → ["배우자", "급여"] (의미 기반 검색으로 "남편 월급"도 매칭 가능)

질문에서 언급된 날짜 정보 (이 정보를 반드시 사용하세요):
- 추출된 날짜: {extracted_date}
- 비교 날짜: {comparison_dates}

중요: 
1. 추출된 날짜 정보가 있으면 반드시 date_info에 반영하세요.
   예: 추출된 날짜가 ({current_year - 1}, 1)이면 date_info는 {{"year": {current_year - 1}, "month": 1}}이어야 합니다.
2. "작년"이라는 표현이 있으면 {current_year - 1}년으로 해석하세요.
3. 현재 년도는 {current_year}년입니다.

JSON만 반환하세요."""

    try:
        messages = [
            SystemMessage(content="당신은 질문 분석 전문가입니다. JSON 형식으로만 응답하세요."),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = llm.invoke(messages)
        analysis_text = response.content.strip()
        
        # JSON 추출 (마크다운 코드 블록 제거)
        if "```json" in analysis_text:
            analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
        elif "```" in analysis_text:
            analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
        
        analysis = json.loads(analysis_text)
        
        # 분석 결과 구조 보장
        if "date_info" not in analysis:
            analysis["date_info"] = {}
        if "filters" not in analysis:
            analysis["filters"] = {}
        if "data_types" not in analysis:
            analysis["data_types"] = []
        if "keywords" not in analysis.get("filters", {}):
            analysis["filters"]["keywords"] = []
        
        # 날짜 정보 보완 (추출된 날짜를 우선시)
        if extracted_date:
            year, month = extracted_date
            # 추출된 날짜를 강제로 설정 (LLM 분석 결과보다 우선)
            analysis["date_info"]["year"] = year
            if month:
                analysis["date_info"]["month"] = month
        
        if comparison_dates:
            date1, date2 = comparison_dates
            # 비교 날짜도 우선시
            if date1[0]:
                analysis["date_info"]["year"] = date1[0]
            if date1[1]:
                analysis["date_info"]["month"] = date1[1]
        
        state["analysis"] = analysis
        
    except Exception as e:
        state["error"] = f"질문 분석 실패: {str(e)}"
        state["analysis"] = {
            "data_types": ["transactions", "monthly_statistics"],
            "date_info": {"year": None, "month": None},
            "filters": {},
            "reasoning": "기본 분석"
        }
    
    return state


def select_tools(state: AgentState) -> AgentState:
    """분석 결과를 바탕으로 필요한 도구 선택"""
    analysis = state.get("analysis") or {}
    data_types = analysis.get("data_types", []) if analysis else []
    
    required_tools = []
    tool_parameters = {}
    
    # 데이터 타입에 따라 도구 선택
    if "transactions" in data_types:
        required_tools.append("get_transactions")
        date_info = analysis.get("date_info", {}) if analysis else {}
        params = {}
        
        # 날짜 범위 설정
        if date_info.get("start_date"):
            params["start_date"] = date_info["start_date"]
        elif date_info.get("end_date"):
            params["end_date"] = date_info["end_date"]
        elif date_info.get("year") and date_info.get("month"):
            # 년도/월을 날짜 범위로 변환
            from datetime import date
            year = date_info["year"]
            month = date_info["month"]
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1)
            else:
                end = date(year, month + 1, 1)
            params["start_date"] = start.strftime("%Y-%m-%d")
            params["end_date"] = (end - timedelta(days=1)).strftime("%Y-%m-%d")
        elif date_info.get("year"):
            # 년도만 있으면 해당 년도 전체
            from datetime import date
            year = date_info["year"]
            params["start_date"] = date(year, 1, 1).strftime("%Y-%m-%d")
            params["end_date"] = date(year, 12, 31).strftime("%Y-%m-%d")
        
        filters = analysis.get("filters", {}) if analysis else {}
        if filters and filters.get("transaction_type"):
            params["transaction_type"] = filters["transaction_type"]
        if filters and filters.get("category_id"):
            params["category_id"] = filters["category_id"]
        
        # keywords가 있으면 더 많이 조회 (필터링 전 충분한 데이터 확보)
        keywords = filters.get("keywords", []) if filters else []
        if keywords:
            params["limit"] = 200  # 키워드 필터링을 위해 더 많이 조회
            params["keywords"] = keywords
        else:
            params["limit"] = 100  # 기본값
        
        tool_parameters["get_transactions"] = params
    
    if "monthly_statistics" in data_types:
        required_tools.append("get_monthly_statistics")
        date_info = analysis.get("date_info", {}) if analysis else {}
        params = {}
        if date_info.get("year"):
            params["year"] = date_info["year"]
        if date_info.get("month"):
            params["month"] = date_info["month"]
        tool_parameters["get_monthly_statistics"] = params
    
    if "category_statistics" in data_types:
        required_tools.append("get_category_statistics")
        date_info = analysis.get("date_info", {}) if analysis else {}
        filters = analysis.get("filters", {}) if analysis else {}
        params = {}
        if date_info.get("year"):
            params["year"] = date_info["year"]
        if date_info.get("month"):
            params["month"] = date_info["month"]
        if filters.get("category_type"):
            params["category_type"] = filters["category_type"]
        tool_parameters["get_category_statistics"] = params
    
    if "categories" in data_types:
        required_tools.append("get_categories")
        tool_parameters["get_categories"] = {}
    
    # 기본적으로 categories는 항상 포함 (카테고리 이름 매핑용)
    if "get_categories" not in required_tools:
        required_tools.append("get_categories")
        tool_parameters["get_categories"] = {}
    
    state["required_tools"] = required_tools
    state["tool_parameters"] = tool_parameters
    
    return state


def collect_data(state: AgentState) -> AgentState:
    """선택된 도구들을 실행하여 데이터 수집"""
    required_tools = state.get("required_tools", [])
    tool_parameters = state.get("tool_parameters", {})
    collected_data = {}
    
    for tool_name in required_tools:
        if tool_name not in TOOL_MAP:
            continue
        
        tool = TOOL_MAP[tool_name]
        params = tool_parameters.get(tool_name, {}).copy()  # 복사본 사용
        
        try:
            result = tool.invoke(params)
            collected_data[tool_name] = result
            
            # 거래 내역 조회 시 키워드 필터링 결과 검증
            if tool_name == "get_transactions" and params.get("keywords"):
                try:
                    transactions = json.loads(result)
                    # 키워드 필터링 결과가 없거나 너무 적으면 키워드 없이 재조회
                    if not isinstance(transactions, list) or len(transactions) == 0:
                        # 키워드 없이 재조회
                        params_without_keywords = params.copy()
                        params_without_keywords.pop("keywords", None)
                        params_without_keywords["limit"] = 100
                        
                        retry_result = tool.invoke(params_without_keywords)
                        collected_data[tool_name] = retry_result
                except (json.JSONDecodeError, TypeError):
                    pass
                    
        except Exception as e:
            collected_data[tool_name] = json.dumps({"error": str(e)})
    
    state["collected_data"] = collected_data
    return state


def build_basic_context(collected_data: Dict, analysis: Dict, date_info: Dict) -> str:
    """기본 컨텍스트 생성 (하드코딩된 로직)"""
    context_parts = []
    
    # 조회된 데이터 요약
    date_summary = []
    if date_info:
        if date_info.get("year"):
            date_summary.append(f"{date_info['year']}년")
        if date_info.get("month"):
            date_summary.append(f"{date_info['month']}월")
    
    if date_summary:
        context_parts.append(f"=== 조회 기간: {' '.join(date_summary)} ===")
        context_parts.append("")
    
    # 카테고리 목록 (항상 먼저 로드)
    category_map = {}
    if "get_categories" in collected_data:
        try:
            categories_data = collected_data["get_categories"]
            if categories_data:
                categories = json.loads(categories_data)
                if isinstance(categories, list):
                    category_map = {cat.get("id"): cat.get("name", "") for cat in categories if isinstance(cat, dict)}
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass
    
    # 월별 통계
    if "get_monthly_statistics" in collected_data:
        try:
            stats_data = collected_data["get_monthly_statistics"]
            if stats_data:
                stats = json.loads(stats_data)
                if isinstance(stats, dict):
                    year = stats.get("year") or (date_info.get("year") if date_info else None) or datetime.now().year
                    month = stats.get("month") or (date_info.get("month") if date_info else None) or datetime.now().month
                    
                    context_parts.append(f"=== {year}년 {month}월 통계 ===")
                    income = float(stats.get("income", 0) or 0)
                    expense = float(stats.get("expense", 0) or 0)
                    balance = float(stats.get("balance", 0) or 0)
                    context_parts.append(f"총 수입: {income:,.0f}원")
                    context_parts.append(f"총 지출: {expense:,.0f}원")
                    context_parts.append(f"잔액: {balance:,.0f}원")
                    context_parts.append("")
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
            pass
    
    # 카테고리별 통계
    if "get_category_statistics" in collected_data:
        try:
            cat_stats_data = collected_data["get_category_statistics"]
            if cat_stats_data:
                cat_stats = json.loads(cat_stats_data)
                if isinstance(cat_stats, list) and cat_stats:
                    year = (date_info.get("year") if date_info else None) or datetime.now().year
                    month = (date_info.get("month") if date_info else None) or datetime.now().month
                    filters = analysis.get("filters", {}) if analysis else {}
                    cat_type = "수입" if filters.get("category_type") == "income" else "지출"
                    context_parts.append(f"=== {year}년 {month}월 카테고리별 {cat_type} ===")
                    for cat in cat_stats[:10]:
                        if isinstance(cat, dict):
                            total = float(cat.get("total", 0) or 0)
                            count = int(cat.get("count", 0) or 0)
                            context_parts.append(
                                f"- {cat.get('category_name', '알 수 없음')}: "
                                f"{total:,.0f}원 ({count}건)"
                            )
                    context_parts.append("")
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
            pass
    
    # 거래 내역
    if "get_transactions" in collected_data:
        try:
            transactions_data = collected_data["get_transactions"]
            if transactions_data:
                transactions = json.loads(transactions_data)
                if isinstance(transactions, list):
                    if transactions:
                        context_parts.append(f"=== 거래 내역 ({len(transactions)}건) ===")
                        for trans in transactions[:30]:
                            if isinstance(trans, dict):
                                trans_date = trans.get("transaction_date", "")
                                trans_type = "수입" if trans.get("type") == "income" else "지출"
                                amount = float(trans.get("amount", 0) or 0)
                                description = trans.get("description", "")
                                category_id = trans.get("category_id")
                                category_name = category_map.get(category_id, "") if category_map else ""
                                
                                # description을 항상 표시 (중요한 정보 포함)
                                context_parts.append(
                                    f"- {trans_date}: {trans_type} {amount:,.0f}원"
                                    + (f" [{category_name}]" if category_name else "")
                                    + (f" - {description}" if description else "")
                                )
                        context_parts.append("")
                    else:
                        # 거래 내역이 없어도 표시 (질문과 관련된 기간임을 알림)
                        year = (date_info.get("year") if date_info else None) or datetime.now().year
                        month = (date_info.get("month") if date_info else None) or datetime.now().month
                        context_parts.append(f"=== {year}년 {month}월 거래 내역 (0건) ===")
                        context_parts.append("경고: 해당 기간에 거래 내역이 조회되지 않았습니다.")
                        context_parts.append("키워드 필터링이 너무 엄격했거나, 해당 기간에 실제로 거래가 없을 수 있습니다.")
                        context_parts.append("")
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
            # 에러가 발생해도 컨텍스트에 포함
            year = (date_info.get("year") if date_info else None) or datetime.now().year
            month = (date_info.get("month") if date_info else None) or datetime.now().month
            context_parts.append(f"=== {year}년 {month}월 거래 내역 조회 오류 ===")
            context_parts.append(f"경고: 거래 내역을 불러오는 중 오류가 발생했습니다: {str(e)}")
            context_parts.append("")
    
    # 카테고리 목록
    if "get_categories" in collected_data:
        try:
            categories_data = collected_data["get_categories"]
            if categories_data:
                categories = json.loads(categories_data)
                if isinstance(categories, list) and categories:
                    income_cats = [c for c in categories if isinstance(c, dict) and c.get("type") == "income"]
                    expense_cats = [c for c in categories if isinstance(c, dict) and c.get("type") == "expense"]
                    
                    context_parts.append("=== 카테고리 목록 ===")
                    if income_cats:
                        context_parts.append("수입 카테고리: " + ", ".join([c.get("name", "") for c in income_cats if isinstance(c, dict)]))
                    if expense_cats:
                        context_parts.append("지출 카테고리: " + ", ".join([c.get("name", "") for c in expense_cats if isinstance(c, dict)]))
                    context_parts.append("")
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
            pass
    
    context_str = "\n".join(context_parts)
    return context_str
    if "get_categories" in collected_data:
        try:
            categories_data = collected_data["get_categories"]
            if categories_data:
                categories = json.loads(categories_data)
                if isinstance(categories, list):
                    category_map = {cat.get("id"): cat.get("name", "") for cat in categories if isinstance(cat, dict)}
                else:
                    category_map = {}
            else:
                category_map = {}
        except (json.JSONDecodeError, TypeError, AttributeError):
            category_map = {}
    else:
        category_map = {}
    
    # 월별 통계
    if "get_monthly_statistics" in collected_data:
        try:
            stats_data = collected_data["get_monthly_statistics"]
            if stats_data:
                stats = json.loads(stats_data)
                if isinstance(stats, dict):
                    year = stats.get("year") or (date_info.get("year") if date_info else None) or datetime.now().year
                    month = stats.get("month") or (date_info.get("month") if date_info else None) or datetime.now().month
                    
                    context_parts.append(f"=== {year}년 {month}월 통계 ===")
                    income = float(stats.get("income", 0) or 0)
                    expense = float(stats.get("expense", 0) or 0)
                    balance = float(stats.get("balance", 0) or 0)
                    context_parts.append(f"총 수입: {income:,.0f}원")
                    context_parts.append(f"총 지출: {expense:,.0f}원")
                    context_parts.append(f"잔액: {balance:,.0f}원")
                    context_parts.append("")
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
            pass
    
    # 카테고리별 통계
    if "get_category_statistics" in collected_data:
        try:
            cat_stats_data = collected_data["get_category_statistics"]
            if cat_stats_data:
                cat_stats = json.loads(cat_stats_data)
                if isinstance(cat_stats, list) and cat_stats:
                    year = (date_info.get("year") if date_info else None) or datetime.now().year
                    month = (date_info.get("month") if date_info else None) or datetime.now().month
                    filters = analysis.get("filters", {}) if analysis else {}
                    cat_type = "수입" if filters.get("category_type") == "income" else "지출"
                    context_parts.append(f"=== {year}년 {month}월 카테고리별 {cat_type} ===")
                    for cat in cat_stats[:10]:
                        if isinstance(cat, dict):
                            total = float(cat.get("total", 0) or 0)
                            count = int(cat.get("count", 0) or 0)
                            context_parts.append(
                                f"- {cat.get('category_name', '알 수 없음')}: "
                                f"{total:,.0f}원 ({count}건)"
                            )
                    context_parts.append("")
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
            pass
    
    # 거래 내역
    if "get_transactions" in collected_data:
        try:
            transactions_data = collected_data["get_transactions"]
            if transactions_data:
                transactions = json.loads(transactions_data)
                if isinstance(transactions, list):
                    if transactions:
                        context_parts.append(f"=== 거래 내역 ({len(transactions)}건) ===")
                        for trans in transactions[:30]:
                            if isinstance(trans, dict):
                                trans_date = trans.get("transaction_date", "")
                                trans_type = "수입" if trans.get("type") == "income" else "지출"
                                amount = float(trans.get("amount", 0) or 0)
                                description = trans.get("description", "")
                                category_id = trans.get("category_id")
                                category_name = category_map.get(category_id, "") if category_map else ""
                                
                                # description을 항상 표시 (중요한 정보 포함)
                                context_parts.append(
                                    f"- {trans_date}: {trans_type} {amount:,.0f}원"
                                    + (f" [{category_name}]" if category_name else "")
                                    + (f" - {description}" if description else "")
                                )
                        context_parts.append("")
                    else:
                        # 거래 내역이 없어도 표시 (질문과 관련된 기간임을 알림)
                        year = (date_info.get("year") if date_info else None) or datetime.now().year
                        month = (date_info.get("month") if date_info else None) or datetime.now().month
                        context_parts.append(f"=== {year}년 {month}월 거래 내역 (0건) ===")
                        context_parts.append("경고: 해당 기간에 거래 내역이 조회되지 않았습니다.")
                        context_parts.append("키워드 필터링이 너무 엄격했거나, 해당 기간에 실제로 거래가 없을 수 있습니다.")
                        context_parts.append("")
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
            # 에러가 발생해도 컨텍스트에 포함
            year = (date_info.get("year") if date_info else None) or datetime.now().year
            month = (date_info.get("month") if date_info else None) or datetime.now().month
            context_parts.append(f"=== {year}년 {month}월 거래 내역 조회 오류 ===")
            context_parts.append(f"경고: 거래 내역을 불러오는 중 오류가 발생했습니다: {str(e)}")
            context_parts.append("")
    
    # 카테고리 목록
    if "get_categories" in collected_data:
        try:
            categories_data = collected_data["get_categories"]
            if categories_data:
                categories = json.loads(categories_data)
                if isinstance(categories, list) and categories:
                    income_cats = [c for c in categories if isinstance(c, dict) and c.get("type") == "income"]
                    expense_cats = [c for c in categories if isinstance(c, dict) and c.get("type") == "expense"]
                    
                    context_parts.append("=== 카테고리 목록 ===")
                    if income_cats:
                        context_parts.append("수입 카테고리: " + ", ".join([c.get("name", "") for c in income_cats if isinstance(c, dict)]))
                    if expense_cats:
                        context_parts.append("지출 카테고리: " + ", ".join([c.get("name", "") for c in expense_cats if isinstance(c, dict)]))
                    context_parts.append("")
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
            pass
    
    context_str = "\n".join(context_parts)
    return context_str


def optimize_context_with_llm(
    llm: Any,
    question: str,
    basic_context: str,
    collected_data: Dict,
    analysis: Dict,
    current_year: int
) -> str:
    """LLM이 컨텍스트를 질문에 맞게 최적화"""
    try:
        # 조회된 데이터 요약
        data_summary = []
        if "get_transactions" in collected_data:
            try:
                transactions = json.loads(collected_data["get_transactions"])
                if isinstance(transactions, list):
                    data_summary.append(f"거래 내역: {len(transactions)}건")
            except:
                pass
        
        if "get_monthly_statistics" in collected_data:
            try:
                stats = json.loads(collected_data["get_monthly_statistics"])
                if isinstance(stats, dict):
                    data_summary.append(f"통계: 수입 {stats.get('income', 0):,.0f}원, 지출 {stats.get('expense', 0):,.0f}원")
            except:
                pass
        
        date_info = analysis.get("date_info", {}) if analysis else {}
        date_str = ""
        if date_info.get("year"):
            date_str += f"{date_info['year']}년 "
        if date_info.get("month"):
            date_str += f"{date_info['month']}월"
        
        optimization_prompt = f"""사용자 질문: {question}

현재 년도: {current_year}년
- '재작년'은 {current_year - 2}년을 의미합니다
- '작년'은 {current_year - 1}년을 의미합니다

조회 기간: {date_str.strip() if date_str else '미지정'}
조회된 데이터: {', '.join(data_summary) if data_summary else '없음'}

기본 컨텍스트:
{basic_context}

위 컨텍스트를 사용자 질문에 최적화하여 재구성하세요:

1. 질문과 직접 관련된 정보만 포함하세요
2. 날짜 정보가 정확한지 확인하세요 (예: "재작년"은 {current_year - 2}년, "작년"은 {current_year - 1}년)
3. 질문에서 요청한 특정 정보(예: "남편 월급")를 강조하세요
4. 불필요한 정보는 제거하거나 간소화하세요
5. 거래 내역의 description 필드를 특히 주의 깊게 확인하세요

최적화된 컨텍스트만 반환하세요. 기존 형식(=== 섹션 ===)을 유지하되, 내용을 질문에 맞게 조정하세요."""

        messages = [
            SystemMessage(content="당신은 컨텍스트 최적화 전문가입니다. 사용자 질문에 맞게 컨텍스트를 재구성하세요."),
            HumanMessage(content=optimization_prompt)
        ]
        
        response = llm.invoke(messages)
        optimized_context = response.content.strip()
        
        # 마크다운 코드 블록 제거
        if "```" in optimized_context:
            lines = optimized_context.split("\n")
            optimized_context = "\n".join([line for line in lines if not line.strip().startswith("```")])
        
        return optimized_context
        
    except Exception as e:
        # LLM 최적화 실패 시 기본 컨텍스트 반환
        return basic_context


def build_context(state: AgentState, llm: Any = None) -> AgentState:
    """조회된 데이터를 컨텍스트 문자열로 변환 (LLM 최적화 포함)"""
    collected_data = state.get("collected_data", {})
    analysis = state.get("analysis") or {}
    date_info = analysis.get("date_info", {}) if analysis else {}
    question = state.get("question", "")
    
    # 기본 컨텍스트 생성
    basic_context = build_basic_context(collected_data, analysis, date_info)
    
    # LLM이 있으면 컨텍스트 최적화 시도
    if llm:
        current_year = datetime.now().year
        optimized_context = optimize_context_with_llm(
            llm, question, basic_context, collected_data, analysis, current_year
        )
        state["context"] = optimized_context
    else:
        state["context"] = basic_context
    
    return state


def generate_response(state: AgentState, llm: Any = None) -> AgentState:
    """최종 LLM 응답 생성"""
    question = state["question"]
    context = state.get("context", "")
    messages = state.get("messages", [])
    
    # llm이 매개변수로 전달되지 않으면 state에서 가져오기 시도
    if llm is None:
        llm = state.get("llm")
    
    if not llm:
        state["error"] = "LLM이 초기화되지 않았습니다."
        return state
    
    # 현재 년도 정보
    current_year = datetime.now().year
    
    # 시스템 프롬프트
    system_prompt = f"""당신은 AI 가계부 어시스턴트입니다. 사용자의 가계부 데이터를 분석하고 질문에 답변하는 역할을 합니다.

중요: 현재 년도 정보
- 현재 년도: {current_year}년
- 사용자가 "재작년"이라고 하면 {current_year - 2}년을 의미합니다
- 사용자가 "재작년 1월"이라고 하면 {current_year - 2}년 1월을 의미합니다
- 사용자가 "작년"이라고 하면 {current_year - 1}년을 의미합니다
- 사용자가 "작년 1월"이라고 하면 {current_year - 1}년 1월을 의미합니다

주요 기능:
1. 거래 내역 요약 및 분석
2. 지출 패턴 분석
3. 통계 데이터 해석
4. 가계부 관리 조언 제공
5. 카테고리별 지출 분석

응답 시 다음 사항을 지켜주세요:
- 한국어로 친절하고 명확하게 답변
- 데이터를 기반으로 구체적인 수치를 제시
- 필요시 거래 내역이나 통계를 참조하여 설명
- 실용적이고 도움이 되는 조언 제공
- 사용자가 이해하기 쉽게 설명
- 컨텍스트에 제공된 데이터를 정확히 참조하여 답변
- 거래 내역의 description 필드를 주의 깊게 확인 (예: "남편 월급", "아내 월급" 등)

중요: 
- 컨텍스트에 제공된 거래 내역을 꼼꼼히 확인하세요
- description 필드에 질문과 관련된 키워드가 있는지 확인하세요
- 통계가 0원이어도 거래 내역에 데이터가 있을 수 있습니다
- 컨텍스트에 표시된 날짜 정보를 정확히 참조하세요
- "작년"이라는 표현이 사용된 경우, 실제 년도({current_year - 1}년)를 명시하여 답변하세요

가계부 데이터는 아래 컨텍스트에 포함되어 있습니다."""
    
    # 컨텍스트에서 날짜 정보 추출 (사용자에게 명확히 전달)
    context_date_info = ""
    if "조회 기간:" in context:
        # 컨텍스트에서 조회 기간 추출
        lines = context.split("\n")
        for line in lines:
            if "조회 기간:" in line:
                context_date_info = line.replace("=== 조회 기간:", "").replace("===", "").strip()
                break
    
    # 프롬프트 구성
    prompt = f"""{system_prompt}

=== 가계부 데이터 컨텍스트 ===
{context}
=== 컨텍스트 끝 ===

사용자 질문: {question}

위의 가계부 데이터를 참고하여 사용자의 질문에 답변해주세요.

중요 지시사항:
1. 컨텍스트에 표시된 조회 기간을 정확히 참조하세요
2. 거래 내역의 description 필드를 특히 주의 깊게 확인하세요
3. "재작년"이라는 표현이 사용된 경우, 실제 년도({current_year - 2}년)를 명시하여 답변하세요
4. "작년"이라는 표현이 사용된 경우, 실제 년도({current_year - 1}년)를 명시하여 답변하세요
5. 컨텍스트에 거래 내역이 포함되어 있다면, 그 정보를 바탕으로 정확한 답변을 제공하세요
6. 데이터가 없는 경우에만 "데이터가 없습니다"라고 답변하세요
7. 컨텍스트의 날짜 정보가 질문과 일치하는지 확인하세요 (예: "재작년" 질문에 2024년 데이터가 있어야 함)"""
    
    try:
        # 대화 히스토리 구성
        llm_messages = [SystemMessage(content=system_prompt)]
        
        # 이전 대화 추가 (최근 5개만)
        for msg in messages[-5:]:
            if msg["role"] == "user":
                llm_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                llm_messages.append(AIMessage(content=msg["content"]))
        
        # 현재 질문 추가
        llm_messages.append(HumanMessage(content=prompt))
        
        # LLM 호출
        response = llm.invoke(llm_messages)
        state["response"] = response.content
        
    except Exception as e:
        state["error"] = f"응답 생성 실패: {str(e)}"
        state["response"] = f"오류가 발생했습니다: {str(e)}"
    
    return state


def create_agent_graph(lmstudio_url: str, model: str = ""):
    """LangGraph Agent 생성"""
    llm = create_llm(lmstudio_url, model)
    
    # 노드 함수들을 클로저로 만들어 llm에 접근할 수 있도록 함
    def analyze_question_with_llm(state: AgentState) -> AgentState:
        return analyze_question(state, llm)
    
    def build_context_with_llm(state: AgentState) -> AgentState:
        return build_context(state, llm)
    
    def generate_response_with_llm(state: AgentState) -> AgentState:
        return generate_response(state, llm)
    
    # 그래프 생성
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("analyze_question", analyze_question_with_llm)
    workflow.add_node("select_tools", select_tools)
    workflow.add_node("collect_data", collect_data)
    workflow.add_node("build_context", build_context_with_llm)
    workflow.add_node("generate_response", generate_response_with_llm)
    
    # 엣지 추가
    workflow.set_entry_point("analyze_question")
    workflow.add_edge("analyze_question", "select_tools")
    workflow.add_edge("select_tools", "collect_data")
    workflow.add_edge("collect_data", "build_context")
    workflow.add_edge("build_context", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # 컴파일
    app = workflow.compile()
    
    return app, llm


def run_agent(
    question: str,
    messages: List[Dict[str, str]],
    lmstudio_url: str,
    model: str = ""
) -> Dict[str, Any]:
    """Agent 실행"""
    app, llm = create_agent_graph(lmstudio_url, model)
    
    # 초기 상태 (llm은 state에 포함하지 않음 - 클로저로 전달)
    initial_state = {
        "question": question,
        "analysis": None,
        "required_tools": [],
        "tool_parameters": {},
        "collected_data": {},
        "context": "",
        "response": "",
        "messages": messages,
        "error": None
    }
    
    # 실행
    try:
        result = app.invoke(initial_state)
        return result
    except Exception as e:
        return {
            **initial_state,
            "error": str(e),
            "response": f"오류가 발생했습니다: {str(e)}"
        }


def stream_agent_response(
    question: str,
    messages: List[Dict[str, str]],
    lmstudio_url: str,
    model: str = ""
):
    """Agent 실행 (스트리밍)"""
    app, llm = create_agent_graph(lmstudio_url, model)
    
    # 초기 상태 (llm은 state에 포함하지 않음 - 클로저로 전달)
    initial_state = {
        "question": question,
        "analysis": None,
        "required_tools": [],
        "tool_parameters": {},
        "collected_data": {},
        "context": "",
        "response": "",
        "messages": messages,
        "error": None
    }
    
    # 스트리밍 실행
    try:
        for chunk in app.stream(initial_state):
            # 각 노드의 출력을 yield
            for node_name, node_output in chunk.items():
                if node_name == "generate_response" and "response" in node_output:
                    # 응답 생성 단계에서는 LLM 스트리밍을 별도로 처리
                    # 여기서는 전체 응답을 받은 후 스트리밍
                    pass
            yield chunk
    except Exception as e:
        yield {
            "error": {"error": str(e), "response": f"오류가 발생했습니다: {str(e)}"}
        }
