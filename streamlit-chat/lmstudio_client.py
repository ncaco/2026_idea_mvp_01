import httpx
import json
import os
from typing import Generator
from datetime import datetime

# #region agent log
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

def stream_lmstudio_response(
    lmstudio_url: str,
    model: str,
    prompt: str,
    timeout: float = 300.0
) -> Generator[str, None, None]:
    """
    LM Studio API를 사용하여 스트리밍 응답을 생성합니다.
    
    Args:
        lmstudio_url: LM Studio 서버 URL (예: http://127.0.0.1:1234)
        model: 사용할 모델 이름
        prompt: 프롬프트 텍스트
        timeout: 요청 타임아웃 (초)
    
    Yields:
        str: 스트리밍 응답 청크
    """
    api_url = f"{lmstudio_url}/v1/chat/completions"
    
    # OpenAI 호환 형식으로 요청 구성
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": True,
        "temperature": 0.7
    }
    
    # #region agent log
    _log("debug-session", "run1", "C", "lmstudio_client.py:stream_lmstudio_response", "함수 진입", {"lmstudio_url": lmstudio_url, "model": model, "api_url": api_url, "prompt_length": len(prompt)})
    # #endregion
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # #region agent log
        _log("debug-session", "run1", "C", "lmstudio_client.py:stream_lmstudio_response", "LM Studio 요청 전", {"payload_model": payload["model"]})
        # #endregion
        
        with httpx.stream(
            "POST",
            api_url,
            json=payload,
            headers=headers,
            timeout=timeout
        ) as response:
            # #region agent log
            _log("debug-session", "run1", "C", "lmstudio_client.py:stream_lmstudio_response", "LM Studio 응답 수신", {"status_code": response.status_code})
            # #endregion
            
            response.raise_for_status()
            
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    # SSE 형식: "data: {...}" 또는 "data: [DONE]"
                    if line.startswith("data: "):
                        data_str = line[6:]  # "data: " 제거
                        if data_str == "[DONE]":
                            # #region agent log
                            _log("debug-session", "run1", "C", "lmstudio_client.py:stream_lmstudio_response", "스트리밍 완료", {"total_chunks": chunk_count})
                            # #endregion
                            break
                        
                        try:
                            data = json.loads(data_str)
                            # OpenAI 형식: choices[0].delta.content
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    chunk_count += 1
                                    # #region agent log
                                    if chunk_count <= 3 or chunk_count % 10 == 0:
                                        _log("debug-session", "run1", "C", "lmstudio_client.py:stream_lmstudio_response", "청크 수신", {"chunk_count": chunk_count, "chunk_length": len(content)})
                                    # #endregion
                                    yield content
                        except json.JSONDecodeError:
                            continue
                        
    except httpx.ConnectError as e:
        # #region agent log
        _log("debug-session", "run1", "C", "lmstudio_client.py:stream_lmstudio_response", "연결 오류", {"error": str(e), "lmstudio_url": lmstudio_url})
        # #endregion
        raise ConnectionError(
            f"LM Studio 서버에 연결할 수 없습니다. "
            f"LM Studio가 {lmstudio_url}에서 실행 중인지 확인하세요."
        )
    except httpx.TimeoutException as e:
        # #region agent log
        _log("debug-session", "run1", "C", "lmstudio_client.py:stream_lmstudio_response", "타임아웃 오류", {"error": str(e)})
        # #endregion
        raise TimeoutError("요청 시간이 초과되었습니다.")
    except httpx.HTTPStatusError as e:
        # #region agent log
        _log("debug-session", "run1", "C", "lmstudio_client.py:stream_lmstudio_response", "HTTP 오류", {"status_code": e.response.status_code, "error": e.response.text})
        # #endregion
        raise Exception(f"HTTP 오류: {e.response.status_code} - {e.response.text}")
