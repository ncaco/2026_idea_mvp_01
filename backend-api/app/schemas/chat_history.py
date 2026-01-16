"""
채팅 히스토리 스키마
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChatMessageBase(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessage(ChatMessageBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessage]
    total: int


class ChatHistorySaveRequest(BaseModel):
    messages: List[ChatMessageBase]
