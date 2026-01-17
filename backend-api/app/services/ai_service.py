"""
AI 서비스 - 자동 카테고리 분류 및 자연어 처리
"""
import os
import re
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import Integer
from app.models import Category, Transaction


def classify_category_by_description(
    db: Session,
    description: str,
    user_id: int,
    transaction_type: str = "expense"
) -> Optional[Dict[str, Any]]:
    """
    거래 설명을 기반으로 카테고리를 자동 분류
    
    Args:
        db: 데이터베이스 세션
        description: 거래 설명
        user_id: 사용자 ID
        transaction_type: 거래 유형 ('income' or 'expense')
    
    Returns:
        추천 카테고리 정보 또는 None
    """
    if not description:
        return None
    
    description_lower = description.lower()
    
    # 사용자의 기존 카테고리 목록 가져오기
    categories = db.query(Category).filter(
        Category.user_id == user_id,
        Category.type == transaction_type
    ).all()
    
    if not categories:
        return None
    
    # 키워드 기반 매칭 (간단한 규칙 기반 분류)
    # 실제로는 OpenAI API나 더 정교한 ML 모델을 사용할 수 있음
    category_keywords = {
        "식비": ["식당", "음식", "카페", "커피", "점심", "저녁", "배달", "치킨", "피자", "햄버거", "라면", "김밥"],
        "교통비": ["지하철", "버스", "택시", "기차", "비행기", "주차", "주유", "휘발유", "주차장", "교통카드"],
        "쇼핑": ["마트", "편의점", "온라인", "쇼핑", "구매", "아마존", "쿠팡", "옷", "신발", "가전"],
        "의료비": ["병원", "약국", "의료", "치과", "검진", "약", "진료"],
        "교육비": ["학원", "교육", "책", "강의", "수강", "학습"],
        "통신비": ["통신", "전화", "인터넷", "핸드폰", "요금", "통신사"],
        "공과금": ["전기", "가스", "수도", "관리비", "공과금", "요금"],
        "기타 지출": []
    }
    
    # 설명에서 키워드 매칭
    best_match = None
    best_score = 0
    
    for category in categories:
        category_name = category.name
        keywords = category_keywords.get(category_name, [])
        
        # 키워드 매칭 점수 계산
        score = 0
        for keyword in keywords:
            if keyword in description_lower:
                score += 1
        
        # 카테고리 이름이 설명에 포함되어 있는지 확인
        if category_name.lower() in description_lower:
            score += 2
        
        if score > best_score:
            best_score = score
            best_match = category
    
    # 최소 점수 이상일 때만 추천
    if best_match and best_score > 0:
        return {
            "category_id": best_match.id,
            "category_name": best_match.name,
            "confidence": min(best_score / 5.0, 1.0)  # 0.0 ~ 1.0
        }
    
    return None


def parse_natural_language(
    text: str,
    user_id: int,
    db: Session
) -> Dict[str, Any]:
    """
    자연어 텍스트에서 거래 정보 추출
    
    예: "어제 점심에 15000원 식비"
    
    Args:
        text: 자연어 입력 텍스트
        user_id: 사용자 ID
        db: 데이터베이스 세션
    
    Returns:
        추출된 거래 정보
    """
    result = {
        "transaction_date": None,
        "amount": None,
        "category_id": None,
        "category_name": None,
        "description": text,
        "type": "expense"
    }
    
    # 날짜 추출
    today = datetime.now().date()
    
    # 상대적 날짜 패턴
    date_patterns = [
        (r"오늘", today),
        (r"어제", today - timedelta(days=1)),
        (r"그저께|그제", today - timedelta(days=2)),
        (r"(\d+)일\s*전", lambda m: today - timedelta(days=int(m.group(1)))),
        (r"(\d+)일\s*후", lambda m: today + timedelta(days=int(m.group(1)))),
    ]
    
    for pattern, value in date_patterns:
        match = re.search(pattern, text)
        if match:
            if callable(value):
                result["transaction_date"] = value(match)
            else:
                result["transaction_date"] = value
            break
    
    # 절대 날짜 패턴 (YYYY-MM-DD, YYYY/MM/DD, MM/DD 등)
    if not result["transaction_date"]:
        date_patterns_abs = [
            r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})",
            r"(\d{1,2})[-/](\d{1,2})",
        ]
        for pattern in date_patterns_abs:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.groups()) == 3:
                        year, month, day = map(int, match.groups())
                        result["transaction_date"] = datetime(year, month, day).date()
                    elif len(match.groups()) == 2:
                        month, day = map(int, match.groups())
                        year = today.year
                        result["transaction_date"] = datetime(year, month, day).date()
                    break
                except ValueError:
                    continue
    
    # 기본값: 오늘
    if not result["transaction_date"]:
        result["transaction_date"] = today
    
    # 금액 추출
    amount_patterns = [
        (r"(\d+(?:,\d{3})*)\s*원", lambda m: int(m.group(1).replace(",", ""))),
        (r"(\d+(?:,\d{3})*)\s*만\s*원", lambda m: int(m.group(1).replace(",", "")) * 10000),
        (r"(\d+(?:,\d{3})*)\s*천\s*원", lambda m: int(m.group(1).replace(",", "")) * 1000),
        (r"만\s*(\d+)\s*원", lambda m: int(m.group(1)) * 10000),
        (r"(\d+)\s*만", lambda m: int(m.group(1)) * 10000),
        (r"(\d+)\s*천", lambda m: int(m.group(1)) * 1000),
        (r"(\d+(?:\.\d+)?)\s*만", lambda m: int(float(m.group(1)) * 10000)),
    ]
    
    for pattern, converter in amount_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                result["amount"] = converter(match)
                break
            except (ValueError, AttributeError):
                continue
    
    # 카테고리 추출
    categories = db.query(Category).filter(Category.user_id == user_id).all()
    category_match = classify_category_by_description(db, text, user_id, "expense")
    
    if category_match:
        result["category_id"] = category_match["category_id"]
        result["category_name"] = category_match["category_name"]
    
    # 수입/지출 판단
    income_keywords = ["수입", "급여", "용돈", "보너스", "환급", "환불"]
    if any(keyword in text for keyword in income_keywords):
        result["type"] = "income"
        # 수입 카테고리로 다시 검색
        category_match = classify_category_by_description(db, text, user_id, "income")
        if category_match:
            result["category_id"] = category_match["category_id"]
            result["category_name"] = category_match["category_name"]
    
    return result


def analyze_spending_patterns(
    db: Session,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    지출 패턴 분석
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        start_date: 시작 날짜
        end_date: 종료 날짜
    
    Returns:
        패턴 분석 결과
    """
    from sqlalchemy import func, extract
    
    if not start_date:
        start_date = datetime.now() - timedelta(days=90)  # 최근 3개월
    if not end_date:
        end_date = datetime.now()
    
    # 월별 지출 패턴
    monthly_expenses = db.query(
        extract('year', Transaction.transaction_date).label('year'),
        extract('month', Transaction.transaction_date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.transaction_date >= start_date.date(),
        Transaction.transaction_date <= end_date.date()
    ).group_by(
        extract('year', Transaction.transaction_date),
        extract('month', Transaction.transaction_date)
    ).all()
    
    # 요일별 지출 패턴 (SQLite용 - strftime 사용)
    # SQLite의 strftime('%w', date)는 0=일요일, 6=토요일
    # 우리는 0=월요일로 변환: CASE 문 사용
    from sqlalchemy import case, Integer
    
    weekday_expenses = db.query(
        case(
            (func.cast(func.strftime('%w', Transaction.transaction_date), Integer) == 0, 6),  # 일요일 -> 6
            else_=(func.cast(func.strftime('%w', Transaction.transaction_date), Integer) - 1)  # 월~토 -> 0~5
        ).label('weekday'),
        func.avg(Transaction.amount).label('avg_amount'),
        func.count(Transaction.id).label('count')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.transaction_date >= start_date.date(),
        Transaction.transaction_date <= end_date.date()
    ).group_by(
        case(
            (func.cast(func.strftime('%w', Transaction.transaction_date), Integer) == 0, 6),
            else_=(func.cast(func.strftime('%w', Transaction.transaction_date), Integer) - 1)
        )
    ).all()
    
    # 이상치 탐지 (평균 대비 2배 이상인 거래)
    avg_amount = db.query(func.avg(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.transaction_date >= start_date.date(),
        Transaction.transaction_date <= end_date.date()
    ).scalar() or 0
    
    threshold = float(avg_amount) * 2 if avg_amount else 0
    
    outliers = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.transaction_date >= start_date.date(),
        Transaction.transaction_date <= end_date.date(),
        Transaction.amount > threshold
    ).order_by(Transaction.amount.desc()).limit(10).all()
    
    return {
        "monthly_pattern": [
            {
                "year": int(row.year),
                "month": int(row.month),
                "total": float(row.total) if row.total else 0
            }
            for row in monthly_expenses
        ],
        "weekday_pattern": [
            {
                "weekday": int(row.weekday),
                "weekday_name": ["월", "화", "수", "목", "금", "토", "일"][int(row.weekday)],
                "avg_amount": float(row.avg_amount) if row.avg_amount else 0,
                "count": int(row.count)
            }
            for row in weekday_expenses
        ],
        "outliers": [
            {
                "id": t.id,
                "date": t.transaction_date.isoformat(),
                "amount": float(t.amount),
                "description": t.description,
                "category_id": t.category_id
            }
            for t in outliers
        ],
        "average_amount": float(avg_amount) if avg_amount else 0,
        "threshold": threshold
    }
