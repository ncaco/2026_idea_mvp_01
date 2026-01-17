from pydantic import BaseModel
from typing import Optional


class TransactionAttachmentBase(BaseModel):
    file_name: str
    file_size: int
    mime_type: str


class TransactionAttachment(TransactionAttachmentBase):
    id: int
    transaction_id: int
    user_id: int
    file_path: str
    created_at: str

    class Config:
        from_attributes = True
