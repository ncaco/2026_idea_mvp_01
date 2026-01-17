from pydantic import BaseModel
from typing import Optional, List


class TagBase(BaseModel):
    name: str
    color: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class Tag(TagBase):
    id: int
    user_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TagWithCount(Tag):
    transaction_count: int = 0
