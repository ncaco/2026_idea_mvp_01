"""
채팅 로그 기록 유틸리티
사용자 입력, 모델 프롬프트, 모델 답변을 기록
"""
import json
import os
from datetime import datetime
from typing import Optional

# 채팅 로그 저장 경로
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chat_logs")
LOG_FILE = os.path.join(LOG_DIR, "chat_logs.jsonl")  # JSONL 형식 (한 줄에 하나의 JSON)

def ensure_log_dir():
    """로그 디렉토리가 존재하는지 확인하고 없으면 생성"""
    os.makedirs(LOG_DIR, exist_ok=True)

def log_chat_interaction(
    user_input: str,
    model_prompt: str,
    model_response: str,
    model_name: Optional[str] = None,
    lmstudio_url: Optional[str] = None,
    context_length: Optional[int] = None,
    response_length: Optional[int] = None,
    error: Optional[str] = None
):
    """
    채팅 상호작용을 로그 파일에 기록
    
    Args:
        user_input: 사용자 입력
        model_prompt: 모델에 전달된 전체 프롬프트
        model_response: 모델 응답
        model_name: 사용된 모델 이름
        lmstudio_url: LM Studio URL
        context_length: 컨텍스트 길이
        response_length: 응답 길이
        error: 오류 메시지 (있는 경우)
    """
    try:
        ensure_log_dir()
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "model_prompt": model_prompt,
            "model_response": model_response,
            "model_name": model_name,
            "lmstudio_url": lmstudio_url,
            "context_length": context_length,
            "response_length": response_length,
            "error": error
        }
        
        # JSONL 형식으로 추가 (append mode)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            f.flush()
            
    except Exception as e:
        print(f"채팅 로그 기록 실패: {e}")

def get_recent_logs(limit: int = 50) -> list:
    """
    최근 채팅 로그를 불러오기
    
    Args:
        limit: 불러올 로그 개수
    
    Returns:
        List[Dict]: 로그 엔트리 리스트
    """
    try:
        if not os.path.exists(LOG_FILE):
            return []
        
        logs = []
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # 최근 limit개만 가져오기
            for line in lines[-limit:]:
                try:
                    logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return logs
    except Exception as e:
        print(f"채팅 로그 불러오기 실패: {e}")
        return []

def clear_logs():
    """채팅 로그 삭제"""
    try:
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        return True
    except Exception as e:
        print(f"채팅 로그 삭제 실패: {e}")
        return False
