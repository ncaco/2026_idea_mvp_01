"""
채팅 히스토리 서비스
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models import ChatHistory
from app.schemas.chat_history import ChatMessageBase


def get_chat_history(
    db: Session,
    user_id: int,
    limit: int = 100
) -> List[ChatHistory]:
    """사용자의 채팅 히스토리 조회"""
    return db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).order_by(desc(ChatHistory.created_at)).limit(limit).all()


def save_chat_messages(
    db: Session,
    user_id: int,
    messages: List[ChatMessageBase]
) -> List[ChatHistory]:
    """채팅 메시지 저장"""
    chat_history_list = []
    for msg in messages:
        chat_history = ChatHistory(
            user_id=user_id,
            role=msg.role,
            content=msg.content
        )
        db.add(chat_history)
        chat_history_list.append(chat_history)
    
    db.commit()
    for ch in chat_history_list:
        db.refresh(ch)
    
    return chat_history_list


def clear_chat_history(
    db: Session,
    user_id: int
) -> int:
    """사용자의 채팅 히스토리 삭제"""
    deleted_count = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).delete()
    db.commit()
    return deleted_count
