"""
인증 및 보안 관련 유틸리티
"""
import warnings
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

# bcrypt 버전 경고 숨기기 (passlib과 bcrypt 호환성 문제로 인한 경고)
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = "your-secret-key-change-in-production"  # 프로덕션에서는 환경변수로 관리
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30일

# OAuth2 스키마
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """현재 로그인한 사용자 조회"""
    import logging
    logger = logging.getLogger(__name__)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logger.info(f"=== get_current_user 호출 ===")
    logger.info(f"토큰 존재 여부: {token is not None}")
    if token:
        logger.info(f"토큰 길이: {len(token)}")
        logger.info(f"토큰 처음 20자: {token[:20]}...")
    
    try:
        logger.info(f"JWT 디코딩 시도...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"JWT 디코딩 성공: {payload}")
        # JWT 표준에 따라 sub는 문자열이므로 정수로 변환
        user_id_str = payload.get("sub")
        logger.info(f"추출된 user_id (문자열): {user_id_str}")
        if user_id_str is None:
            logger.error("user_id가 None입니다!")
            raise credentials_exception
        user_id: int = int(user_id_str)
        logger.info(f"변환된 user_id (정수): {user_id}")
    except JWTError as e:
        logger.error(f"JWT 디코딩 오류: {type(e).__name__}: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"예상치 못한 오류: {type(e).__name__}: {str(e)}")
        raise credentials_exception
    
    logger.info(f"DB에서 사용자 조회 시도: user_id={user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.error(f"사용자를 찾을 수 없습니다: user_id={user_id}")
        raise credentials_exception
    logger.info(f"사용자 조회 성공: username={user.username}, id={user.id}")
    return user
