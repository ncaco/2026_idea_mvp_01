"""
채팅 히스토리 저장 및 불러오기 유틸리티
로컬 파일 시스템에 JSON 형식으로 저장
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# 채팅 히스토리 저장 경로
HISTORY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chat_history")
HISTORY_FILE = os.path.join(HISTORY_DIR, "chat_history.json")

def ensure_history_dir():
    """히스토리 디렉토리가 존재하는지 확인하고 없으면 생성"""
    os.makedirs(HISTORY_DIR, exist_ok=True)

def save_messages(messages: List[Dict]) -> bool:
    """
    메시지 히스토리를 파일에 저장
    
    Args:
        messages: 메시지 리스트 (role, content 포함)
    
    Returns:
        bool: 저장 성공 여부
    """
    try:
        ensure_history_dir()
        history_data = {
            "messages": messages,
            "last_updated": datetime.now().isoformat()
        }
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"채팅 히스토리 저장 실패: {e}")
        return False

def load_messages() -> List[Dict]:
    """
    저장된 메시지 히스토리를 불러오기
    
    Returns:
        List[Dict]: 메시지 리스트
    """
    try:
        if not os.path.exists(HISTORY_FILE):
            return []
        
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history_data = json.load(f)
            return history_data.get("messages", [])
    except Exception as e:
        print(f"채팅 히스토리 불러오기 실패: {e}")
        return []

def clear_history() -> bool:
    """
    채팅 히스토리 삭제
    
    Returns:
        bool: 삭제 성공 여부
    """
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        return True
    except Exception as e:
        print(f"채팅 히스토리 삭제 실패: {e}")
        return False
