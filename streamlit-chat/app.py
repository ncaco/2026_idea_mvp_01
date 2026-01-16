import streamlit as st
import json
import os
from datetime import datetime
from lmstudio_client import stream_lmstudio_response
from api_client import get_accountbook_context
from prompts import build_prompt
from chat_history import save_messages, load_messages, clear_history
from chat_logger import log_chat_interaction

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

# 페이지 설정
st.set_page_config(
    page_title="AI 가계부 채팅",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }  # 모든 메뉴 항목 제거
)

# 커스텀 CSS로 디자인 개선
st.markdown("""
<style>
    /* Streamlit 헤더 메뉴 숨기기 */
    #MainMenu {
        visibility: hidden !important;
        height: 0 !important;
        display: none !important;
    }
    
    header[data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0 !important;
        display: none !important;
    }
    
    /* Deploy 버튼 숨기기 */
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* 설정 메뉴 버튼들 숨기기 */
    button[title="View app source"],
    button[title="Get help"],
    button[title="Report a bug"],
    button[title="About"],
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* 헤더 영역 전체 숨기기 */
    div[data-testid="stHeader"],
    section[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* 모든 레벨에서 스크롤 제거 */
    html, body {
        height: 100vh !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    #root {
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    .main {
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    /* 메인 컨테이너 - flexbox 레이아웃, 정확한 높이 */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 100% !important;
        width: 100% !important;
        height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
        margin: 0 auto !important;
    }
    
    /* 사이드바가 있을 때 메인 영역 조정 */
    .main:has([data-testid="stSidebar"]) .block-container {
        padding-left: 1rem !important;
    }
    
    /* 제목과 캡션 고정 */
    h1 {
        margin-bottom: 0.25rem !important;
        flex-shrink: 0 !important;
        font-size: 1.5rem !important;
    }
    
    .stCaption {
        flex-shrink: 0 !important;
        margin-bottom: 0.75rem !important;
        font-size: 0.875rem !important;
    }
    
    /* 채팅 메시지 영역 - 스크롤 가능, 나머지 공간 차지 */
    .main .block-container > div[data-testid="stVerticalBlock"]:not(:has([data-testid="stChatInput"])) {
        flex: 1 1 auto !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        min-height: 0 !important;
        max-height: none !important;
        padding-right: 0.5rem !important;
    }
    
    /* 입력 필드가 있는 블록 - 고정 */
    .main .block-container > div[data-testid="stVerticalBlock"]:has([data-testid="stChatInput"]) {
        flex: 0 0 auto !important;
        overflow: visible !important;
        max-height: none !important;
        padding-top: 0.5rem !important;
        border-top: 1px solid #e5e7eb !important;
        background-color: white !important;
        position: sticky !important;
        bottom: 0 !important;
        z-index: 100 !important;
    }
    
    /* 채팅 메시지 스타일 */
    [data-testid="stChatMessage"] {
        padding: 0.75rem !important;
        margin-bottom: 0.5rem !important;
        border-radius: 0.5rem !important;
    }
    
    /* 사용자 메시지 */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageUser"]) {
        background-color: #f3f4f6 !important;
    }
    
    /* AI 메시지 */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAssistant"]) {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
    }
    
    /* Info 메시지 스타일 */
    [data-testid="stMarkdownContainer"] {
        padding: 0.5rem 0 !important;
    }
    
    /* 스크롤바 스타일 */
    .main .block-container > div[data-testid="stVerticalBlock"]::-webkit-scrollbar {
        width: 6px !important;
    }
    
    .main .block-container > div[data-testid="stVerticalBlock"]::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        border-radius: 3px !important;
    }
    
    .main .block-container > div[data-testid="stVerticalBlock"]::-webkit-scrollbar-thumb {
        background: #c1c1c1 !important;
        border-radius: 3px !important;
    }
    
    .main .block-container > div[data-testid="stVerticalBlock"]::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8 !important;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    # 저장된 히스토리 불러오기
    saved_messages = load_messages()
    st.session_state.messages = saved_messages if saved_messages else []

if "lmstudio_url" not in st.session_state:
    st.session_state.lmstudio_url = "http://127.0.0.1:1234"

if "model" not in st.session_state:
    st.session_state.model = ""

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = True

if "show_logs" not in st.session_state:
    st.session_state.show_logs = False

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")
    st.session_state.lmstudio_url = st.text_input(
        "LM Studio URL",
        value=st.session_state.lmstudio_url,
        help="LM Studio 서버 주소"
    )
    st.session_state.model = st.text_input(
        "모델 이름",
        value=st.session_state.model,
        help="LM Studio에서 로드한 모델 이름"
    )
    
    st.divider()
    
    if st.button("대화 초기화", use_container_width=True):
        st.session_state.messages = []
        clear_history()
        st.success("대화가 초기화되었습니다.")
        st.rerun()
    
    st.divider()
    
    # 히스토리 정보
    if st.session_state.messages:
        st.caption(f"💾 저장된 대화: {len(st.session_state.messages)}개 메시지")
        if st.button("히스토리 삭제", use_container_width=True, type="secondary"):
            clear_history()
            st.session_state.messages = []
            st.success("히스토리가 삭제되었습니다.")
            st.rerun()
    
    st.divider()
    
    # 채팅 로그 정보
    from chat_logger import get_recent_logs
    recent_logs = get_recent_logs(limit=10)
    if recent_logs:
        st.caption(f"📝 채팅 로그: {len(recent_logs)}개 기록")
        if st.button("로그 보기", use_container_width=True, type="secondary"):
            st.session_state.show_logs = not st.session_state.get("show_logs", False)
    
    if st.session_state.get("show_logs", False):
        st.markdown("### 최근 채팅 로그")
        for i, log in enumerate(reversed(recent_logs[-5:])):  # 최근 5개만 표시
            with st.expander(f"로그 {i+1} - {log.get('timestamp', '')[:19]}"):
                st.text("사용자 입력:")
                st.code(log.get('user_input', ''), language='text')
                st.text("모델 프롬프트:")
                st.code(log.get('model_prompt', '')[:500] + '...' if len(log.get('model_prompt', '')) > 500 else log.get('model_prompt', ''), language='text')
                st.text("모델 응답:")
                st.code(log.get('model_response', '')[:500] + '...' if len(log.get('model_response', '')) > 500 else log.get('model_response', ''), language='text')
                if log.get('error'):
                    st.error(f"오류: {log.get('error')}")

# 메인 영역
st.title("💬 AI 가계부 채팅")
st.caption("가계부 데이터를 기반으로 질문하고 답변을 받아보세요.")

# 채팅 메시지 영역 (스크롤 가능)
if st.session_state.messages:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
else:
    st.info("👋 안녕하세요! 가계부에 대해 궁금한 것을 물어보세요.")
    st.markdown("""
    **예시 질문:**
    - 이번 달 지출은 얼마인가요?
    - 가장 많이 지출한 카테고리는 무엇인가요?
    - 최근 거래 내역을 알려주세요.
    - 지출 패턴을 분석해주세요.
    """)

# 사용자 입력
if prompt := st.chat_input("질문을 입력하세요..."):
    # #region agent log
    _log("debug-session", "run1", "D", "app.py:chat_input", "사용자 입력 수신", {"prompt": prompt[:100]})
    # #endregion
    
                # 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 사용자 메시지 저장
    save_messages(st.session_state.messages)
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            try:
                # 가계부 컨텍스트 수집
                # #region agent log
                _log("debug-session", "run1", "D", "app.py:chat_input", "컨텍스트 수집 시작", {})
                # #endregion
                context = get_accountbook_context(user_question=prompt)
                
                # #region agent log
                _log("debug-session", "run1", "D", "app.py:chat_input", "컨텍스트 수집 완료", {"context_length": len(context)})
                # #endregion
                
                # 프롬프트 구성
                full_prompt = build_prompt(prompt, context)
                
                # #region agent log
                _log("debug-session", "run1", "D", "app.py:chat_input", "프롬프트 구성 완료", {"full_prompt_length": len(full_prompt), "lmstudio_url": st.session_state.lmstudio_url, "model": st.session_state.model})
                # #endregion
                
                # 스트리밍 응답 생성
                response_placeholder = st.empty()
                full_response = ""
                
                # #region agent log
                _log("debug-session", "run1", "D", "app.py:chat_input", "스트리밍 시작", {})
                # #endregion
                
                for chunk in stream_lmstudio_response(
                    st.session_state.lmstudio_url,
                    st.session_state.model,
                    full_prompt
                ):
                    if chunk:
                        full_response += chunk
                        response_placeholder.markdown(full_response + "▌")
                
                # #region agent log
                _log("debug-session", "run1", "D", "app.py:chat_input", "스트리밍 완료", {"response_length": len(full_response)})
                # #endregion
                
                # 최종 응답 표시
                response_placeholder.markdown(full_response)
                
                # 메시지 히스토리에 추가
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })
                
                # 히스토리 저장
                save_messages(st.session_state.messages)
                
                # 채팅 로그 기록
                log_chat_interaction(
                    user_input=prompt,
                    model_prompt=full_prompt,
                    model_response=full_response,
                    model_name=st.session_state.model,
                    lmstudio_url=st.session_state.lmstudio_url,
                    context_length=len(context),
                    response_length=len(full_response)
                )
                
            except Exception as e:
                # #region agent log
                _log("debug-session", "run1", "D", "app.py:chat_input", "오류 발생", {"error": str(e), "error_type": type(e).__name__})
                # #endregion
                error_message = f"오류가 발생했습니다: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
                
                # 오류 로그 기록
                try:
                    context = get_accountbook_context()
                    full_prompt = build_prompt(prompt, context)
                    log_chat_interaction(
                        user_input=prompt,
                        model_prompt=full_prompt,
                        model_response="",
                        model_name=st.session_state.model,
                        lmstudio_url=st.session_state.lmstudio_url,
                        error=str(e)
                    )
                except:
                    pass
