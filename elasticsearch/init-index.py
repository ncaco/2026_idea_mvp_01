"""
엘라스틱서치 인덱스 초기화 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend-api"))

from elasticsearch import Elasticsearch
import json

# 엘라스틱서치 클라이언트 초기화
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
es = Elasticsearch([ES_HOST], request_timeout=30)

INDEX_NAME = "transactions"

# 인덱스 매핑 정의
INDEX_MAPPING = {
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
            "type": {"type": "keyword"},  # "income" or "expense"
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
                "dims": 768,
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
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "korean": {
                    "type": "standard"  # 기본 분석기 사용 (nori 플러그인 없이)
                }
            }
        }
    }
}


def create_index():
    """인덱스 생성"""
    try:
        # 기존 인덱스가 있으면 삭제
        if es.indices.exists(index=INDEX_NAME):
            print(f"기존 인덱스 '{INDEX_NAME}' 삭제 중...")
            es.indices.delete(index=INDEX_NAME)
        
        # 새 인덱스 생성
        print(f"인덱스 '{INDEX_NAME}' 생성 중...")
        es.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)
        print(f"인덱스 '{INDEX_NAME}' 생성 완료!")
        
        # 인덱스 정보 출력
        try:
            index_info = es.indices.get(index=INDEX_NAME)
            # 엘라스틱서치 8.x 응답 객체를 딕셔너리로 변환
            if hasattr(index_info, 'body'):
                index_info_dict = index_info.body
            elif hasattr(index_info, 'to_dict'):
                index_info_dict = index_info.to_dict()
            else:
                index_info_dict = dict(index_info) if isinstance(index_info, dict) else str(index_info)
            
            print(f"\n인덱스 정보:")
            print(json.dumps(index_info_dict, indent=2, ensure_ascii=False))
        except Exception as info_error:
            # 인덱스 정보 출력 실패해도 인덱스 생성은 성공했으므로 계속 진행
            print(f"\n인덱스 정보 출력 실패 (인덱스는 생성됨): {info_error}")
        
        return True
    except Exception as e:
        print(f"인덱스 생성 실패: {e}")
        return False


def check_connection():
    """엘라스틱서치 연결 확인"""
    try:
        if es.ping():
            cluster_info = es.info()
            # 엘라스틱서치 8.x 응답 객체를 딕셔너리로 변환
            if hasattr(cluster_info, 'body'):
                cluster_info_dict = cluster_info.body
            elif hasattr(cluster_info, 'to_dict'):
                cluster_info_dict = cluster_info.to_dict()
            else:
                cluster_info_dict = dict(cluster_info) if isinstance(cluster_info, dict) else {}
            
            print(f"엘라스틱서치 연결 성공!")
            print(f"클러스터 이름: {cluster_info_dict.get('cluster_name', 'N/A')}")
            print(f"버전: {cluster_info_dict.get('version', {}).get('number', 'N/A')}")
            return True
        else:
            print("엘라스틱서치 연결 실패")
            return False
    except Exception as e:
        print(f"엘라스틱서치 연결 오류: {e}")
        print(f"엘라스틱서치가 실행 중인지 확인하세요: {ES_HOST}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("엘라스틱서치 인덱스 초기화")
    print("=" * 50)
    
    if not check_connection():
        sys.exit(1)
    
    if create_index():
        print("\n인덱스 초기화 완료!")
    else:
        print("\n인덱스 초기화 실패!")
        sys.exit(1)
