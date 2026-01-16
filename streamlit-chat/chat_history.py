"""
채팅 히스토리 저장 및 불러오기 유틸리티
백엔드 API를 통해 사용자별로 저장/조회
"""
import os
from typing import List, Dict, Optional
import httpx
from api_client import API_BASE_URL

# JWT 토큰 (환경 변수 또는 쿼리 파라미터에서 가져옴)
def get_auth_token() -> Optional[str]:
    """인증 토큰 가져오기"""
    # 1. 환경 변수에서 가져오기
    token = os.getenv("AUTH_TOKEN")
    if token:
        return token
    
    # 2. Streamlit 쿼리 파라미터에서 가져오기 (나중에 구현)
    # import streamlit as st
    # if hasattr(st, 'query_params') and 'token' in st.query_params:
    #     return st.query_params['token']
    
    return None

def get_headers() -> Dict[str, str]:
    """API 요청 헤더 생성"""
    headers = {"Content-Type": "application/json"}
    token = get_auth_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def save_messages(messages: List[Dict]) -> bool:
    """
    메시지 히스토리를 백엔드 API에 저장
    
    Args:
        messages: 메시지 리스트 (role, content 포함)
    
    Returns:
        bool: 저장 성공 여부
    """
    try:
        # 토큰이 없으면 로컬 파일에 저장 (하위 호환성)
        if not get_auth_token():
            return _save_messages_local(messages)
        
        response = httpx.post(
            f"{API_BASE_URL}/api/chat-history/",
            json={"messages": messages},
            headers=get_headers(),
            timeout=10.0
        )
        
        if response.status_code == 200:
            return True
        else:
            # API 실패 시 로컬 파일에 저장 (폴백)
            print(f"API 저장 실패 ({response.status_code}), 로컬 파일에 저장: {response.text}")
            return _save_messages_local(messages)
    except Exception as e:
        print(f"채팅 히스토리 저장 실패: {e}")
        # API 실패 시 로컬 파일에 저장 (폴백)
        return _save_messages_local(messages)

def load_messages() -> List[Dict]:
    """
    저장된 메시지 히스토리를 백엔드 API에서 불러오기
    
    Returns:
        List[Dict]: 메시지 리스트
    """
    try:
        # 토큰이 없으면 로컬 파일에서 불러오기 (하위 호환성)
        if not get_auth_token():
            return _load_messages_local()
        
        response = httpx.get(
            f"{API_BASE_URL}/api/chat-history/",
            headers=get_headers(),
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            # ChatMessage 객체를 Dict로 변환
            messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in data.get("messages", [])
            ]
            return messages
        elif response.status_code == 401:
            # 인증 실패 시 로컬 파일에서 불러오기
            print("인증 실패, 로컬 파일에서 불러오기")
            return _load_messages_local()
        else:
            print(f"API 조회 실패 ({response.status_code}): {response.text}")
            return _load_messages_local()
    except Exception as e:
        print(f"채팅 히스토리 불러오기 실패: {e}")
        return _load_messages_local()

def clear_history() -> bool:
    """
    채팅 히스토리 삭제
    
    Returns:
        bool: 삭제 성공 여부
    """
    try:
        # 토큰이 없으면 로컬 파일 삭제 (하위 호환성)
        if not get_auth_token():
            return _clear_history_local()
        
        response = httpx.delete(
            f"{API_BASE_URL}/api/chat-history/",
            headers=get_headers(),
            timeout=10.0
        )
        
        if response.status_code == 200:
            return True
        else:
            # API 실패 시 로컬 파일 삭제 (폴백)
            print(f"API 삭제 실패 ({response.status_code}), 로컬 파일 삭제: {response.text}")
            return _clear_history_local()
    except Exception as e:
        print(f"채팅 히스토리 삭제 실패: {e}")
        return _clear_history_local()

# 로컬 파일 저장 (하위 호환성 및 폴백)
import json
from datetime import datetime

HISTORY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chat_history")
HISTORY_FILE = os.path.join(HISTORY_DIR, "chat_history.json")

def _ensure_history_dir():
    """히스토리 디렉토리가 존재하는지 확인하고 없으면 생성"""
    os.makedirs(HISTORY_DIR, exist_ok=True)

def _save_messages_local(messages: List[Dict]) -> bool:
    """로컬 파일에 저장 (하위 호환성)"""
    try:
        _ensure_history_dir()
        history_data = {
            "messages": messages,
            "last_updated": datetime.now().isoformat()
        }
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"로컬 파일 저장 실패: {e}")
        return False

def _load_messages_local() -> List[Dict]:
    """로컬 파일에서 불러오기 (하위 호환성)"""
    try:
        if not os.path.exists(HISTORY_FILE):
            return []
        
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history_data = json.load(f)
            return history_data.get("messages", [])
    except Exception as e:
        print(f"로컬 파일 불러오기 실패: {e}")
        return []

def _clear_history_local() -> bool:
    """로컬 파일 삭제 (하위 호환성)"""
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        return True
    except Exception as e:
        print(f"로컬 파일 삭제 실패: {e}")
        return False
