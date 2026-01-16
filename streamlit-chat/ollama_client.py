import httpx
import json
import os
from typing import Generator
from datetime import datetime

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

def stream_ollama_response(
    ollama_url: str,
    model: str,
    prompt: str,
    timeout: float = 300.0
) -> Generator[str, None, None]:
    """
    Ollama API를 사용하여 스트리밍 응답을 생성합니다.
    
    Args:
        ollama_url: Ollama 서버 URL (예: http://localhost:11434)
        model: 사용할 모델 이름 (예: llama2, mistral)
        prompt: 프롬프트 텍스트
        timeout: 요청 타임아웃 (초)
    
    Yields:
        str: 스트리밍 응답 청크
    """
    api_url = f"{ollama_url}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    
    # #region agent log
    _log("debug-session", "run1", "C", "ollama_client.py:stream_ollama_response", "함수 진입", {"ollama_url": ollama_url, "model": model, "api_url": api_url, "prompt_length": len(prompt)})
    # #endregion
    
    try:
        # #region agent log
        _log("debug-session", "run1", "C", "ollama_client.py:stream_ollama_response", "Ollama 요청 전", {"payload_model": payload["model"]})
        # #endregion
        
        with httpx.stream(
            "POST",
            api_url,
            json=payload,
            timeout=timeout
        ) as response:
            # #region agent log
            _log("debug-session", "run1", "C", "ollama_client.py:stream_ollama_response", "Ollama 응답 수신", {"status_code": response.status_code})
            # #endregion
            
            response.raise_for_status()
            
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            chunk_count += 1
                            # #region agent log
                            if chunk_count <= 3 or chunk_count % 10 == 0:
                                _log("debug-session", "run1", "C", "ollama_client.py:stream_ollama_response", "청크 수신", {"chunk_count": chunk_count, "chunk_length": len(data["response"])})
                            # #endregion
                            yield data["response"]
                        if data.get("done", False):
                            # #region agent log
                            _log("debug-session", "run1", "C", "ollama_client.py:stream_ollama_response", "스트리밍 완료", {"total_chunks": chunk_count})
                            # #endregion
                            break
                    except json.JSONDecodeError:
                        continue
                        
    except httpx.ConnectError as e:
        # #region agent log
        _log("debug-session", "run1", "C", "ollama_client.py:stream_ollama_response", "연결 오류", {"error": str(e), "ollama_url": ollama_url})
        # #endregion
        raise ConnectionError(
            f"Ollama 서버에 연결할 수 없습니다. "
            f"Ollama가 {ollama_url}에서 실행 중인지 확인하세요."
        )
    except httpx.TimeoutException as e:
        # #region agent log
        _log("debug-session", "run1", "C", "ollama_client.py:stream_ollama_response", "타임아웃 오류", {"error": str(e)})
        # #endregion
        raise TimeoutError("요청 시간이 초과되었습니다.")
    except httpx.HTTPStatusError as e:
        # #region agent log
        _log("debug-session", "run1", "C", "ollama_client.py:stream_ollama_response", "HTTP 오류", {"status_code": e.response.status_code, "error": e.response.text})
        # #endregion
        raise Exception(f"HTTP 오류: {e.response.status_code} - {e.response.text}")
