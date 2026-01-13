# AI 가계부 - Windows 애플리케이션

## 프로젝트 개요

AI 기능이 포함된 윈도우 데스크톱 가계부 애플리케이션입니다. 수입과 지출을 효율적으로 관리하고, AI를 통해 자동 카테고리 분류, 지출 패턴 분석, 예산 추천 등의 기능을 제공합니다.

## 주요 기능

### 기본 기능
- ✅ 수입/지출 등록 및 관리
- ✅ 카테고리별 분류
- ✅ 월별/연도별 통계 및 차트
- ✅ 검색 및 필터링

### AI 기능
- 🤖 **자동 카테고리 분류**: 거래 내역을 입력하면 AI가 자동으로 카테고리를 추천
- 📊 **지출 패턴 분석**: 사용자의 지출 패턴을 분석하여 인사이트 제공
- 💡 **예산 추천**: 과거 데이터를 기반으로 적정 예산 제안
- 🔮 **지출 예측**: 다음 달 예상 지출액 예측
- 💬 **자연어 입력**: "오늘 커피 5000원" 같은 자연어로 거래 입력

## 기술 스택

### 프론트엔드
- **Electron**: 윈도우 데스크톱 애플리케이션
- **React**: UI 프레임워크
- **TypeScript**: 타입 안정성
- **Tailwind CSS**: 스타일링
- **Chart.js / Recharts**: 차트 라이브러리

### 백엔드
- **Spring Boot**: REST API 서버
- **SQLite**: 경량 파일 기반 데이터베이스 (별도 설치 불필요)
- **JPA/Hibernate**: ORM

### AI/ML
- **Python FastAPI**: AI 서비스 (별도 마이크로서비스)
- **OpenAI API / Local LLM**: 자연어 처리 및 카테고리 분류
- **Python scikit-learn**: 지출 패턴 분석 및 예측

## 프로젝트 구조

```
2026_idea_mvp_01/
├── frontend/              # Electron + React 프론트엔드
│   ├── src/
│   │   ├── main/         # Electron 메인 프로세스
│   │   ├── renderer/     # React 앱
│   │   └── preload/      # Preload 스크립트
│   ├── package.json
│   └── electron-builder.json
│
├── backend/               # Spring Boot 백엔드
│   ├── src/main/java/
│   ├── src/main/resources/
│   └── build.gradle
│
├── ai-service/            # Python AI 서비스
│   ├── app/
│   ├── requirements.txt
│   └── main.py
│
├── data/                  # SQLite 데이터베이스 파일 저장 위치
│   └── accountbook.db     # SQLite 데이터베이스 파일
│
├── db_structure.md        # 데이터베이스 스키마
├── project_specs.md       # 프로젝트 명세 및 작업 추적
└── README.md
```

## 개발 환경 설정

### 필수 요구사항
- Node.js 18+
- Java 17+
- Python 3.10+
- SQLite (Spring Boot에서 자동 포함, 별도 설치 불필요)

### 설치 및 실행

#### 1. 프론트엔드 (Electron + React)
```powershell
cd ./frontend
npm install
npm run dev          # 개발 모드
npm run build        # 빌드
npm run dist         # 윈도우 설치 파일 생성
```

#### 2. 백엔드 (Spring Boot)
```powershell
cd ./backend
./gradlew bootRun    # 또는 gradlew.bat bootRun
```

#### 3. AI 서비스 (Python FastAPI)
```powershell
cd ./ai-service
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

## 데이터베이스 스키마

자세한 스키마는 `db_structure.md` 파일을 참고하세요.

### 주요 테이블
- `transactions`: 거래 내역 (수입/지출)
- `categories`: 카테고리
- `budgets`: 예산
- `users`: 사용자

## AI 기능 상세

### 1. 자동 카테고리 분류
- 거래 내역의 설명(메모)을 분석하여 적절한 카테고리 추천
- 예: "스타벅스 강남점" → "음식/카페"

### 2. 지출 패턴 분석
- 월별/요일별/시간대별 지출 패턴 분석
- 카테고리별 지출 트렌드 분석
- 비정상 지출 감지 및 알림

### 3. 예산 추천
- 과거 3개월 데이터 기반으로 다음 달 예산 제안
- 카테고리별 예산 분배 제안

### 4. 지출 예측
- 시계열 분석을 통한 다음 달 예상 지출액 예측
- 계절성, 트렌드 고려

### 5. 자연어 입력
- "오늘 점심 15000원", "월급 300만원" 같은 자연어 입력 처리
- 날짜, 금액, 카테고리 자동 추출

## 개발 로드맵

### Phase 1: 기본 기능 (MVP)
- [ ] 프로젝트 구조 설정
- [ ] 데이터베이스 스키마 설계
- [ ] 기본 CRUD 기능 (수입/지출 등록, 조회, 수정, 삭제)
- [ ] 카테고리 관리
- [ ] 기본 통계 및 차트

### Phase 2: AI 기능 추가
- [ ] AI 서비스 구축
- [ ] 자동 카테고리 분류
- [ ] 자연어 입력 처리
- [ ] 지출 패턴 분석

### Phase 3: 고급 기능
- [ ] 예산 관리 및 추천
- [ ] 지출 예측
- [ ] 리포트 생성
- [ ] 데이터 내보내기/가져오기

### Phase 4: 최적화 및 배포
- [ ] 성능 최적화
- [ ] UI/UX 개선
- [ ] 윈도우 설치 파일 패키징
- [ ] 자동 업데이트 기능

## 라이선스

MIT License
