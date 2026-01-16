"""
채팅 히스토리 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.chat_history import (
    ChatHistoryResponse,
    ChatHistorySaveRequest,
    ChatMessage
)
from app.services.chat_history_service import (
    get_chat_history,
    save_chat_messages,
    clear_chat_history
)

router = APIRouter()


@router.get("/", response_model=ChatHistoryResponse)
def get_user_chat_history(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자의 채팅 히스토리 조회"""
    try:
        history = get_chat_history(db, current_user.id, limit)
        messages = [
            ChatMessage(
                id=ch.id,
                user_id=ch.user_id,
                role=ch.role,
                content=ch.content,
                created_at=ch.created_at
            )
            for ch in reversed(history)  # 오래된 것부터
        ]
        return ChatHistoryResponse(messages=messages, total=len(messages))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 실패: {str(e)}")


@router.post("/")
def save_user_chat_history(
    request: ChatHistorySaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자의 채팅 히스토리 저장"""
    try:
        # 기존 히스토리 삭제 후 새로 저장 (간단한 구현)
        # 실제로는 증분 저장이 더 효율적이지만, 여기서는 전체 교체 방식 사용
        clear_chat_history(db, current_user.id)
        saved_messages = save_chat_messages(db, current_user.id, request.messages)
        return {
            "message": "채팅 히스토리가 저장되었습니다",
            "saved_count": len(saved_messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 저장 실패: {str(e)}")


@router.delete("/")
def delete_user_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자의 채팅 히스토리 삭제"""
    try:
        deleted_count = clear_chat_history(db, current_user.id)
        return {
            "message": "채팅 히스토리가 삭제되었습니다",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 삭제 실패: {str(e)}")
