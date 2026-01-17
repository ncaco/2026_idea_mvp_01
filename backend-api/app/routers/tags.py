from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.tag import Tag, TagCreate, TagUpdate
from app.services import tag_service

router = APIRouter()


@router.get("", response_model=List[Tag])
def get_tags(
    with_count: bool = Query(False, description="거래 수 포함 여부"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """태그 목록 조회"""
    if with_count:
        tags = tag_service.get_tags_with_count(db, current_user.id)
        return tags
    return tag_service.get_tags(db, current_user.id)


@router.get("/{tag_id}", response_model=Tag)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """태그 상세 조회"""
    tag = tag_service.get_tag(db, tag_id, current_user.id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="태그를 찾을 수 없습니다."
        )
    return tag


@router.post("", response_model=Tag, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """태그 생성"""
    try:
        return tag_service.create_tag(db, current_user.id, tag_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{tag_id}", response_model=Tag)
def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """태그 수정"""
    try:
        tag = tag_service.update_tag(db, tag_id, current_user.id, tag_data)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="태그를 찾을 수 없습니다."
            )
        return tag
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """태그 삭제"""
    success = tag_service.delete_tag(db, tag_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="태그를 찾을 수 없습니다."
        )
