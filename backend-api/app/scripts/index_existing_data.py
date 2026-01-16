"""
기존 거래 내역 데이터를 엘라스틱서치에 일괄 인덱싱
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Transaction, Category
from app.services.elasticsearch_service import index_transaction, prepare_document_for_indexing
from app.core.elasticsearch import create_index_if_not_exists, get_elasticsearch_client
from app.services.embedding_service import generate_embeddings_batch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def index_all_transactions():
    """모든 거래 내역을 엘라스틱서치에 인덱싱"""
    db: Session = SessionLocal()
    
    try:
        # 인덱스 생성 확인
        logger.info("인덱스 생성 확인 중...")
        create_index_if_not_exists()
        
        # 모든 거래 내역 조회
        logger.info("거래 내역 조회 중...")
        transactions = db.query(Transaction).all()
        total_count = len(transactions)
        logger.info(f"총 {total_count}개의 거래 내역을 찾았습니다")
        
        if total_count == 0:
            logger.info("인덱싱할 데이터가 없습니다")
            return
        
        # 카테고리 정보를 미리 로드
        categories = {cat.id: cat for cat in db.query(Category).all()}
        
        # 배치로 인덱싱
        batch_size = 100
        success_count = 0
        fail_count = 0
        
        for i in range(0, total_count, batch_size):
            batch = transactions[i:i + batch_size]
            logger.info(f"배치 {i//batch_size + 1} 처리 중... ({i+1}/{total_count})")
            
            for transaction in batch:
                try:
                    category = categories.get(transaction.category_id)
                    if index_transaction(db, transaction, category):
                        success_count += 1
                    else:
                        fail_count += 1
                        logger.warning(f"인덱싱 실패: transaction_id={transaction.id}")
                except Exception as e:
                    fail_count += 1
                    logger.error(f"인덱싱 오류 (transaction_id={transaction.id}): {e}")
            
            logger.info(f"진행 상황: 성공 {success_count}, 실패 {fail_count}")
        
        logger.info("=" * 50)
        logger.info(f"인덱싱 완료!")
        logger.info(f"성공: {success_count}")
        logger.info(f"실패: {fail_count}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"일괄 인덱싱 실패: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("기존 거래 내역 데이터 일괄 인덱싱")
    print("=" * 50)
    
    try:
        index_all_transactions()
        print("\n인덱싱이 완료되었습니다!")
    except Exception as e:
        print(f"\n인덱싱 실패: {e}")
        sys.exit(1)
