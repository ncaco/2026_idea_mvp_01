"""
엘라스틱서치 클라이언트 및 기본 함수
"""
import os
from typing import Dict, List, Optional, Any
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError, NotFoundError
import logging

logger = logging.getLogger(__name__)

# 엘라스틱서치 연결 설정
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", None)
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", None)

# 전역 클라이언트 인스턴스
_es_client: Optional[Elasticsearch] = None

INDEX_NAME = "transactions"


def get_elasticsearch_client() -> Elasticsearch:
    """엘라스틱서치 클라이언트 싱글톤 반환"""
    global _es_client
    
    if _es_client is None:
        config = {
            "hosts": [ES_HOST],
            "request_timeout": 30,
            "max_retries": 3,
            "retry_on_timeout": True
        }
        
        if ES_USERNAME and ES_PASSWORD:
            config["basic_auth"] = (ES_USERNAME, ES_PASSWORD)
        
        _es_client = Elasticsearch(**config)
        
        # 연결 테스트
        try:
            if not _es_client.ping():
                logger.error("엘라스틱서치 연결 실패")
                raise ConnectionError("엘라스틱서치에 연결할 수 없습니다")
            logger.info(f"엘라스틱서치 연결 성공: {ES_HOST}")
        except Exception as e:
            logger.error(f"엘라스틱서치 연결 오류: {e}")
            raise
    
    return _es_client


def index_exists() -> bool:
    """인덱스 존재 여부 확인"""
    try:
        es = get_elasticsearch_client()
        return es.indices.exists(index=INDEX_NAME)
    except Exception as e:
        logger.error(f"인덱스 존재 확인 실패: {e}")
        return False


def create_index_if_not_exists():
    """인덱스가 없으면 생성"""
    if index_exists():
        logger.info(f"인덱스 '{INDEX_NAME}'가 이미 존재합니다")
        return True
    
    try:
        es = get_elasticsearch_client()
        
        # 인덱스 매핑 정의
        mapping = {
            "mappings": {
                "properties": {
                    "transaction_id": {"type": "integer"},
                    "user_id": {"type": "integer"},
                    "category_id": {"type": "integer"},
                    "category_name": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "category_color": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "amount": {"type": "float"},
                    "description": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "description_text": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "description_embedding": {
                        "type": "dense_vector",
                        "dims": 768,  # jhgan/ko-sroberta-multitask는 768차원
                        "index": True,
                        "similarity": "cosine"
                    },
                    "transaction_date": {"type": "date"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        es.indices.create(index=INDEX_NAME, body=mapping)
        logger.info(f"인덱스 '{INDEX_NAME}' 생성 완료")
        return True
    except RequestError as e:
        if e.error == "resource_already_exists_exception":
            logger.info(f"인덱스 '{INDEX_NAME}'가 이미 존재합니다")
            return True
        logger.error(f"인덱스 생성 실패: {e}")
        return False
    except Exception as e:
        logger.error(f"인덱스 생성 오류: {e}")
        return False


def hybrid_search(
    query_text: str,
    query_embedding: List[float],
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
    category_id: Optional[int] = None,
    size: int = 20
) -> Dict[str, Any]:
    """
    하이브리드 검색 (BM25 + kNN)
    
    Args:
        query_text: 검색 키워드
        query_embedding: 검색어 벡터 임베딩 (768차원)
        user_id: 사용자 ID
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
        transaction_type: 거래 타입 ("income" or "expense")
        category_id: 카테고리 ID
        size: 반환할 결과 수
    
    Returns:
        검색 결과 딕셔너리
    """
    es = get_elasticsearch_client()
    
    # 필터 조건 구성
    must_filters = [
        {"term": {"user_id": user_id}}
    ]
    
    if start_date:
        must_filters.append({
            "range": {
                "transaction_date": {
                    "gte": start_date
                }
            }
        })
    
    if end_date:
        must_filters.append({
            "range": {
                "transaction_date": {
                    "lte": end_date
                }
            }
        })
    
    if transaction_type:
        must_filters.append({"term": {"type": transaction_type}})
    
    if category_id:
        must_filters.append({"term": {"category_id": category_id}})
    
    # 검색 쿼리 구성 (임베딩이 있으면 하이브리드, 없으면 BM25만)
    should_clauses = [
        # BM25 키워드 검색
        {
            "multi_match": {
                "query": query_text,
                "fields": ["description^2", "description_text", "category_name"],
                "type": "best_fields",
                "fuzziness": "AUTO"
            }
        }
    ]
    
    # 임베딩이 있으면 kNN 벡터 검색 추가
    if query_embedding is not None:
        should_clauses.append({
            "knn": {
                "field": "description_embedding",
                "query_vector": query_embedding,
                "k": size,
                "num_candidates": size * 2
            }
        })
    
    search_query = {
        "size": size,
        "query": {
            "bool": {
                "must": must_filters,
                "should": should_clauses,
                "minimum_should_match": 1
            }
        },
        "_source": [
            "transaction_id",
            "user_id",
            "category_id",
            "category_name",
            "category_color",
            "type",
            "amount",
            "description",
            "transaction_date",
            "created_at",
            "updated_at"
        ]
    }
    
    try:
        response = es.search(index=INDEX_NAME, body=search_query)
        return response
    except Exception as e:
        logger.error(f"하이브리드 검색 실패: {e}")
        raise


def index_document(document: Dict[str, Any]) -> bool:
    """문서 인덱싱"""
    try:
        es = get_elasticsearch_client()
        es.index(
            index=INDEX_NAME,
            id=document.get("transaction_id"),
            document=document
        )
        return True
    except Exception as e:
        logger.error(f"문서 인덱싱 실패: {e}")
        return False


def update_document(transaction_id: int, document: Dict[str, Any]) -> bool:
    """문서 업데이트"""
    try:
        es = get_elasticsearch_client()
        es.update(
            index=INDEX_NAME,
            id=transaction_id,
            body={"doc": document}
        )
        return True
    except NotFoundError:
        # 문서가 없으면 새로 생성
        document["transaction_id"] = transaction_id
        return index_document(document)
    except Exception as e:
        logger.error(f"문서 업데이트 실패: {e}")
        return False


def delete_document(transaction_id: int) -> bool:
    """문서 삭제"""
    try:
        es = get_elasticsearch_client()
        es.delete(index=INDEX_NAME, id=transaction_id)
        return True
    except NotFoundError:
        # 문서가 없어도 성공으로 처리
        return True
    except Exception as e:
        logger.error(f"문서 삭제 실패: {e}")
        return False
