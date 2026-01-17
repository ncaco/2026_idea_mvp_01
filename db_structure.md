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

### 5. recurring_transactions (반복 거래)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 반복 거래 ID |
| user_id | INTEGER | FOREIGN KEY (users.id), NOT NULL | 사용자 ID |
| category_id | INTEGER | FOREIGN KEY (categories.id), NOT NULL | 카테고리 ID |
| type | TEXT | NOT NULL | 타입: 'income' (수입) 또는 'expense' (지출) |
| amount | DECIMAL(10,2) | NOT NULL | 금액 (양수) |
| description | TEXT | | 거래 설명/메모 |
| frequency | TEXT | NOT NULL | 반복 주기: 'daily', 'weekly', 'monthly', 'yearly' |
| day_of_month | INTEGER | | 월의 몇 일 (1-31, NULL이면 매월 마지막 날) |
| day_of_week | INTEGER | | 요일 (0=월요일, 6=일요일, weekly일 때만 사용) |
| start_date | DATE | NOT NULL | 반복 시작일 |
| end_date | DATE | | 반복 종료일 (NULL이면 무제한) |
| is_active | BOOLEAN | NOT NULL, DEFAULT 1 | 활성화 여부 |
| last_generated_date | DATE | | 마지막으로 거래가 생성된 날짜 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 생성일시 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 수정일시 |

## 관계

- `users` 1:N `categories`
- `users` 1:N `transactions`
- `users` 1:N `budgets`
- `users` 1:N `recurring_transactions`
- `users` 1:N `tags`
- `users` 1:N `transaction_templates`
- `categories` 1:N `transactions`
- `categories` 1:N `budgets`
- `categories` 1:N `recurring_transactions`
- `transactions` N:M `tags` (transaction_tags 테이블)
- `transactions` 1:N `transaction_attachments`

## 인덱스

- `transactions.transaction_date`: 거래일자 조회 최적화
- `transactions.user_id`: 사용자별 거래 조회 최적화
- `transactions.category_id`: 카테고리별 거래 조회 최적화
- `categories.user_id`: 사용자별 카테고리 조회 최적화
- `categories.type`: 타입별 카테고리 조회 최적화
- `recurring_transactions.user_id, is_active`: 사용자별 활성 반복 거래 조회 최적화
- `recurring_transactions.start_date`: 시작일 조회 최적화

### 6. tags (태그)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 태그 ID |
| user_id | INTEGER | FOREIGN KEY (users.id), NOT NULL | 사용자 ID |
| name | TEXT | NOT NULL | 태그명 |
| color | TEXT | | 태그 색상 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 생성일시 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 수정일시 |

### 7. transaction_tags (거래-태그 관계)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| transaction_id | INTEGER | PRIMARY KEY, FOREIGN KEY (transactions.id) | 거래 ID |
| tag_id | INTEGER | PRIMARY KEY, FOREIGN KEY (tags.id) | 태그 ID |

### 8. transaction_templates (거래 템플릿)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 템플릿 ID |
| user_id | INTEGER | FOREIGN KEY (users.id), NOT NULL | 사용자 ID |
| category_id | INTEGER | FOREIGN KEY (categories.id), NOT NULL | 카테고리 ID |
| type | TEXT | NOT NULL | 타입: 'income' (수입) 또는 'expense' (지출) |
| amount | DECIMAL(10,2) | NOT NULL | 금액 |
| description | TEXT | | 설명 |
| name | TEXT | NOT NULL | 템플릿 이름 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 생성일시 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 수정일시 |

### 9. transaction_attachments (거래 첨부파일)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 첨부파일 ID |
| transaction_id | INTEGER | FOREIGN KEY (transactions.id), NOT NULL | 거래 ID |
| user_id | INTEGER | FOREIGN KEY (users.id), NOT NULL | 사용자 ID |
| file_name | TEXT | NOT NULL | 파일명 |
| file_path | TEXT | NOT NULL | 파일 경로 |
| file_size | INTEGER | NOT NULL | 파일 크기 (bytes) |
| mime_type | TEXT | NOT NULL | MIME 타입 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 생성일시 |
- `tags.user_id`: 사용자별 태그 조회 최적화
- `transaction_tags.transaction_id`: 거래별 태그 조회 최적화
- `transaction_tags.tag_id`: 태그별 거래 조회 최적화
- `transaction_templates.user_id`: 사용자별 템플릿 조회 최적화
- `transaction_attachments.transaction_id`: 거래별 첨부파일 조회 최적화
- `transaction_attachments.user_id`: 사용자별 첨부파일 조회 최적화
