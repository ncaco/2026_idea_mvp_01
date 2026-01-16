"""
벡터 임베딩 생성 서비스
"""
import os
import random
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# 전역 모델 인스턴스
_embedding_model = None
_model_load_error = None

# 모델 설정
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "jhgan/ko-sroberta-multitask")
# 실제 차원은 모델 로드 후 동적으로 확인
EMBEDDING_DIM = 768  # jhgan/ko-sroberta-multitask는 768차원


def get_embedding_model():
    """임베딩 모델 싱글톤 반환"""
    global _embedding_model, _model_load_error
    
    if _embedding_model is None and _model_load_error is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"임베딩 모델 로딩 중: {MODEL_NAME}")
            _embedding_model = SentenceTransformer(MODEL_NAME)
            logger.info("임베딩 모델 로딩 완료")
        except Exception as e:
            logger.error(f"임베딩 모델 로딩 실패: {e}")
            _model_load_error = str(e)
            # 모델 로드 실패해도 계속 진행 (임베딩 없이 키워드 검색만 사용)
            logger.warning("임베딩 모델이 로드되지 않았습니다. 키워드 검색만 사용됩니다.")
    
    if _model_load_error:
        return None
    
    return _embedding_model


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    텍스트를 벡터 임베딩으로 변환
    
    Args:
        text: 변환할 텍스트
    
    Returns:
        벡터 리스트 또는 None (모델이 로드되지 않은 경우)
    """
    if not text or not text.strip():
        return None
    
    model = get_embedding_model()
    if model is None:
        # 모델이 로드되지 않았으면 None 반환
        return None
    
    try:
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"임베딩 생성 실패: {e}")
        return None


def generate_embeddings_batch(texts: List[str]) -> List[Optional[List[float]]]:
    """
    여러 텍스트를 배치로 벡터 임베딩으로 변환
    
    Args:
        texts: 변환할 텍스트 리스트
    
    Returns:
        벡터 리스트의 리스트 (모델이 로드되지 않은 경우 None 리스트)
    """
    if not texts:
        return []
    
    model = get_embedding_model()
    if model is None:
        # 모델이 로드되지 않았으면 None 리스트 반환
        return [None] * len(texts)
    
    try:
        # 빈 텍스트 필터링
        valid_texts = [t if t and t.strip() else " " for t in texts]
        embeddings = model.encode(valid_texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"배치 임베딩 생성 실패: {e}")
        return [None] * len(texts)
