# 데이터베이스 스키마 (SQLite)

## 개요

SQLite 파일 기반 데이터베이스를 사용합니다. 별도의 데이터베이스 서버 설치 없이 파일로 관리됩니다.
데이터베이스 파일 위치: `data/accountbook.db`

## 테이블 구조

### 1. users (사용자)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**설명**: 사용자 정보를 저장합니다. 현재는 단일 사용자 모드로 설계하지만, 향후 다중 사용자 지원을 위해 준비합니다.

---

### 2. categories (카테고리)
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK(type IN ('INCOME', 'EXPENSE')),
    parent_id INTEGER,
    icon VARCHAR(50),
    color VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);
```

**설명**: 수입/지출 카테고리를 관리합니다. 계층 구조를 지원합니다.
- `type`: 'INCOME' (수입) 또는 'EXPENSE' (지출)
- `parent_id`: 상위 카테고리 ID (NULL이면 최상위 카테고리)
- `icon`: 아이콘 이름 (예: "coffee", "shopping")
- `color`: 카테고리 색상 (HEX 코드)

**기본 카테고리 예시**:
- 수입: 급여, 부수입, 투자수익 등
- 지출: 식비, 교통비, 쇼핑, 의료비, 교육비 등

---

### 3. transactions (거래 내역)
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type VARCHAR(10) NOT NULL CHECK(type IN ('INCOME', 'EXPENSE')),
    amount DECIMAL(15, 2) NOT NULL,
    category_id INTEGER,
    description TEXT,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

**설명**: 모든 수입/지출 거래 내역을 저장합니다.
- `type`: 'INCOME' (수입) 또는 'EXPENSE' (지출)
- `amount`: 금액 (양수로 저장)
- `category_id`: 카테고리 ID (NULL 가능)
- `description`: 거래 설명/메모
- `transaction_date`: 거래 발생 날짜

---

### 4. budgets (예산)
```sql
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER,
    amount DECIMAL(15, 2) NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK(month >= 1 AND month <= 12),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    UNIQUE(user_id, category_id, year, month)
);
```

**설명**: 월별 예산을 관리합니다.
- `category_id`: NULL이면 전체 예산, 특정 카테고리면 해당 카테고리 예산
- `year`, `month`: 예산 적용 연도/월

---

### 5. ai_suggestions (AI 추천 내역)
```sql
CREATE TABLE ai_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,
    suggested_category_id INTEGER,
    confidence DECIMAL(5, 4) NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
    suggestion_type VARCHAR(20) NOT NULL CHECK(suggestion_type IN ('CATEGORY', 'BUDGET', 'PATTERN')),
    suggestion_data TEXT,  -- JSON 형식으로 추가 데이터 저장
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (suggested_category_id) REFERENCES categories(id)
);
```

**설명**: AI가 제공한 추천 내역을 저장합니다.
- `suggestion_type`: 'CATEGORY' (카테고리 추천), 'BUDGET' (예산 추천), 'PATTERN' (패턴 분석)
- `suggestion_data`: JSON 형식으로 추가 정보 저장
- `confidence`: 추천 신뢰도 (0.0 ~ 1.0)

---

## 인덱스

성능 최적화를 위한 인덱스:

```sql
-- 거래 내역 조회 최적화
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date DESC);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_type ON transactions(type);

-- 예산 조회 최적화
CREATE INDEX idx_budgets_user_year_month ON budgets(user_id, year, month);

-- 카테고리 조회 최적화
CREATE INDEX idx_categories_type ON categories(type);
CREATE INDEX idx_categories_parent ON categories(parent_id);
```

---

## 초기 데이터

### 기본 카테고리 데이터

```sql
-- 수입 카테고리
INSERT INTO categories (name, type, icon, color) VALUES
('급여', 'INCOME', 'money', '#4CAF50'),
('부수입', 'INCOME', 'wallet', '#8BC34A'),
('투자수익', 'INCOME', 'trending-up', '#2196F3'),
('기타수입', 'INCOME', 'more', '#9E9E9E');

-- 지출 카테고리
INSERT INTO categories (name, type, icon, color) VALUES
('식비', 'EXPENSE', 'restaurant', '#FF5722'),
('교통비', 'EXPENSE', 'car', '#3F51B5'),
('쇼핑', 'EXPENSE', 'shopping', '#E91E63'),
('의료비', 'EXPENSE', 'medical', '#F44336'),
('교육비', 'EXPENSE', 'school', '#9C27B0'),
('통신비', 'EXPENSE', 'phone', '#00BCD4'),
('주거비', 'EXPENSE', 'home', '#795548'),
('문화생활', 'EXPENSE', 'movie', '#FF9800'),
('기타지출', 'EXPENSE', 'more', '#607D8B');
```

---

## 데이터베이스 초기화

Spring Boot에서 JPA를 사용하여 자동으로 테이블을 생성할 수 있습니다.
또는 `schema.sql` 파일을 사용하여 수동으로 초기화할 수 있습니다.

### application.properties 설정 예시

```properties
# SQLite 설정
spring.datasource.url=jdbc:sqlite:data/accountbook.db
spring.datasource.driver-class-name=org.sqlite.JDBC
spring.jpa.database-platform=org.hibernate.community.dialect.SQLiteDialect
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

---

## 백업 및 복원

SQLite는 파일 기반이므로 간단하게 백업/복원이 가능합니다.

### 백업
```powershell
# 데이터베이스 파일을 복사
Copy-Item data/accountbook.db data/accountbook_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db
```

### 복원
```powershell
# 백업 파일로 복원
Copy-Item data/accountbook_backup_20260101_120000.db data/accountbook.db
```

---

## 마이그레이션

스키마 변경 시:
1. JPA의 `ddl-auto=update`를 사용하여 자동 마이그레이션
2. 또는 Flyway/Liquibase를 사용하여 버전 관리된 마이그레이션
