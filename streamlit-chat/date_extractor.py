"""
사용자 질문에서 날짜 정보를 추출하는 유틸리티
"""
import re
from datetime import datetime
from typing import Optional, Tuple

def extract_date_from_question(question: str) -> Optional[Tuple[int, int]]:
    """
    질문에서 년도와 월을 추출합니다.
    
    Args:
        question: 사용자 질문
    
    Returns:
        (year, month) 튜플 또는 None
    """
    question_lower = question.lower()
    
    # 패턴 1: "재작년", "작년", "2025년 1월" 등 (구체적인 패턴 우선)
    patterns = [
        # "재작년 1월", "재작년1월" (현재 년도 - 2)
        (r'재작년\s*(\d+)월', lambda m: (datetime.now().year - 2, int(m.group(1)))),
        # "재작년"
        (r'재작년', lambda m: (datetime.now().year - 2, None)),
        # "작년 1월", "작년1월" (현재 년도 - 1)
        (r'작년\s*(\d+)월', lambda m: (datetime.now().year - 1, int(m.group(1)))),
        # "작년"
        (r'작년', lambda m: (datetime.now().year - 1, None)),
        # "2025년 1월", "2025년1월"
        (r'(\d{4})년\s*(\d+)월', lambda m: (int(m.group(1)), int(m.group(2)))),
        # "2025년"
        (r'(\d{4})년', lambda m: (int(m.group(1)), None)),
        # "1월" (올해로 가정)
        (r'(\d+)월', lambda m: (datetime.now().year, int(m.group(1)))),
    ]
    
    for pattern, extractor in patterns:
        match = re.search(pattern, question_lower)
        if match:
            try:
                result = extractor(match)
                if result[1] is None:
                    # 월이 없으면 전체 년도 데이터를 의미
                    return (result[0], None)
                return result
            except (ValueError, IndexError):
                continue
    
    return None

def extract_comparison_dates(question: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    비교 질문에서 두 개의 날짜를 추출합니다.
    예: "작년 1월과 올해 1월 비교"
    
    Returns:
        ((year1, month1), (year2, month2)) 또는 None
    """
    # 간단한 구현: 두 개의 날짜 패턴 찾기
    dates = []
    
    # "재작년 1월" 패턴
    two_years_ago_match = re.search(r'재작년\s*(\d+)월', question.lower())
    if two_years_ago_match:
        dates.append((datetime.now().year - 2, int(two_years_ago_match.group(1))))
    
    # "작년 1월" 패턴
    last_year_match = re.search(r'작년\s*(\d+)월', question.lower())
    if last_year_match:
        dates.append((datetime.now().year - 1, int(last_year_match.group(1))))
    
    # "올해 1월", "이번 1월" 패턴
    this_year_match = re.search(r'(올해|이번|올해)\s*(\d+)월', question.lower())
    if this_year_match:
        dates.append((datetime.now().year, int(this_year_match.group(2))))
    
    # "2025년 1월" 패턴
    year_month_match = re.search(r'(\d{4})년\s*(\d+)월', question.lower())
    if year_month_match:
        dates.append((int(year_month_match.group(1)), int(year_month_match.group(2))))
    
    if len(dates) >= 2:
        return (dates[0], dates[1])
    elif len(dates) == 1:
        # 하나만 찾았으면, 다른 하나는 현재 년도/월로 가정
        current = (datetime.now().year, datetime.now().month)
        return (dates[0], current)
    
    return None
