# 데이터베이스 스키마

## 개요

SQLite 데이터베이스를 사용하며, 파일은 `data/accountbook.db`에 저장됩니다.

## 테이블 구조

### 1. users (사용자)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 사용자 ID |
| username | TEXT | UNIQUE, NOT NULL | 사용자명 |
| email | TEXT | UNIQUE | 이메일 (선택사항) |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 생성일시 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 수정일시 |

**Phase 1에서는 단일 사용자만 지원하므로, 기본 사용자 1명만 생성됩니다.**

### 2. categories (카테고리)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 카테고리 ID |
| name | TEXT | NOT NULL | 카테고리명 |
| type | TEXT | NOT NULL | 타입: 'income' (수입) 또는 'expense' (지출) |
| color | TEXT | | 색상 코드 (예: '#FF5733') |
| icon | TEXT | | 아이콘 이름 (선택사항) |
| user_id | INTEGER | FOREIGN KEY (users.id) | 사용자 ID |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 생성일시 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 수정일시 |

**기본 카테고리:**
- 수입: "급여", "용돈", "기타 수입"
- 지출: "식비", "교통비", "쇼핑", "의료비", "교육비", "기타 지출"

### 3. transactions (거래 내역)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 거래 ID |
| user_id | INTEGER | FOREIGN KEY (users.id), NOT NULL | 사용자 ID |
| category_id | INTEGER | FOREIGN KEY (categories.id), NOT NULL | 카테고리 ID |
| type | TEXT | NOT NULL | 타입: 'income' (수입) 또는 'expense' (지출) |
| amount | DECIMAL(10,2) | NOT NULL | 금액 (양수) |
| description | TEXT | | 거래 설명/메모 |
| transaction_date | DATE | NOT NULL | 거래일자 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 생성일시 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 수정일시 |

### 4. budgets (예산)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 예산 ID |
| user_id | INTEGER | FOREIGN KEY (users.id), NOT NULL | 사용자 ID |
| category_id | INTEGER | FOREIGN KEY (categories.id) | 카테고리 ID (NULL이면 전체 예산) |
| amount | DECIMAL(10,2) | NOT NULL | 예산 금액 |
| month | TEXT | NOT NULL | 예산 월 (YYYY-MM 형식) |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 생성일시 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 수정일시 |

**Phase 1에서는 기본 구조만 정의하고, 실제 기능은 Phase 3에서 구현됩니다.**

## 관계

- `users` 1:N `categories`
- `users` 1:N `transactions`
- `users` 1:N `budgets`
- `categories` 1:N `transactions`
- `categories` 1:N `budgets`

## 인덱스

- `transactions.transaction_date`: 거래일자 조회 최적화
- `transactions.user_id`: 사용자별 거래 조회 최적화
- `transactions.category_id`: 카테고리별 거래 조회 최적화
- `categories.user_id`: 사용자별 카테고리 조회 최적화
- `categories.type`: 타입별 카테고리 조회 최적화
