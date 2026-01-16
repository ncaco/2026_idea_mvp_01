"""
LangGraph Agent State 정의
"""
from typing import TypedDict, List, Dict, Optional, Any


class AgentState(TypedDict):
    """Agent의 상태를 관리하는 TypedDict"""
    # 입력
    question: str  # 사용자 질문
    
    # 분석 단계
    analysis: Optional[Dict[str, Any]]  # 질문 분석 결과 (필요한 데이터 타입, 날짜 정보 등)
    
    # 도구 선택 단계
    required_tools: List[str]  # 필요한 도구 목록 (예: ["get_transactions", "get_monthly_statistics"])
    tool_parameters: Dict[str, Dict[str, Any]]  # 각 도구에 필요한 파라미터
    
    # 데이터 수집 단계
    collected_data: Dict[str, Any]  # 조회된 데이터 (도구 이름을 키로 사용)
    
    # 컨텍스트 구성 단계
    context: str  # 최종 컨텍스트 문자열
    
    # 응답 생성 단계
    response: str  # LLM 응답
    
    # 대화 히스토리
    messages: List[Dict[str, str]]  # 대화 히스토리 (role, content)
    
    # 메타데이터
    error: Optional[str]  # 에러 메시지 (있는 경우)
    llm: Optional[Any]  # LLM 인스턴스 (LangGraph state에 포함되지 않으므로 주의)
