# AI 가계부 - 윈도우 애플리케이션

## 프로젝트 개요

AI 기능이 포함된 윈도우 데스크톱 가계부 애플리케이션입니다. Next.js + Electron을 사용하여 웹 기술로 네이티브 윈도우 앱을 구현했습니다. 수입과 지출을 효율적으로 관리하고, AI를 통해 자동 카테고리 분류, 지출 패턴 분석, 예산 추천 등의 기능을 제공합니다.

**배포 옵션**:
- 🖥️ **윈도우 데스크톱 앱**: Electron으로 패키징하여 `.exe` 설치 파일 생성
- 🌐 **웹 애플리케이션**: Next.js를 웹 서버로 배포 (선택사항)

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
- **Next.js**: React 기반 풀스택 프레임워크
- **Electron**: 데스크톱 애플리케이션 프레임워크 (윈도우 앱 빌드)
- **TypeScript**: 타입 안정성
- **Tailwind CSS**: 스타일링
- **Chart.js / Recharts**: 차트 라이브러리
- **React Query / SWR**: 데이터 페칭 및 상태 관리

### 백엔드 (FastAPI 마이크로서비스)
- **FastAPI**: REST API 서버 (백엔드 API 서비스)
- **SQLite**: 경량 파일 기반 데이터베이스 (별도 설치 불필요)
- **SQLAlchemy**: Python ORM
- **Pydantic**: 데이터 검증 및 직렬화

### AI 서비스 (FastAPI 마이크로서비스)
- **FastAPI**: AI 전용 서비스
- **OpenAI API / Local LLM**: 자연어 처리 및 카테고리 분류
- **Python scikit-learn**: 지출 패턴 분석 및 예측
- **NumPy / Pandas**: 데이터 분석

## 프로젝트 구조

```
2026_idea_mvp_01/
├── frontend/              # Next.js + Electron 프론트엔드
│   ├── app/               # Next.js App Router
│   ├── components/        # React 컴포넌트
│   ├── lib/               # 유틸리티 함수
│   ├── public/            # 정적 파일
│   ├── electron/          # Electron 메인 프로세스
│   │   ├── main.js        # Electron 메인 프로세스
│   │   └── preload.js     # Preload 스크립트
│   ├── package.json
│   ├── next.config.js
│   └── electron-builder.json  # Electron 빌드 설정
│
├── backend-api/           # FastAPI 백엔드 API 서비스
│   ├── app/
│   │   ├── main.py        # FastAPI 앱 진입점
│   │   ├── routers/       # API 라우터
│   │   ├── models/        # SQLAlchemy 모델
│   │   ├── schemas/       # Pydantic 스키마
│   │   ├── services/      # 비즈니스 로직
│   │   └── database.py    # 데이터베이스 설정
│   ├── requirements.txt
│   └── .env
│
├── ai-service/            # FastAPI AI 서비스 (마이크로서비스)
│   ├── app/
│   │   ├── main.py        # FastAPI 앱 진입점
│   │   ├── routers/       # AI API 라우터
│   │   ├── services/      # AI 서비스 로직
│   │   │   ├── category_classifier.py
│   │   │   ├── nlp_parser.py
│   │   │   └── pattern_analyzer.py
│   │   └── models/        # ML 모델 (선택사항)
│   ├── requirements.txt
│   └── .env
│
├── data/                  # SQLite 데이터베이스 파일 저장 위치
│   └── accountbook.db     # SQLite 데이터베이스 파일
│
├── db_structure.md        # 데이터베이스 스키마
├── project_specs.md       # 프로젝트 명세 및 작업 추적
└── README.md
```

## 아키텍처 (FastAPI 마이크로서비스 + Electron)

```
┌─────────────────────────┐
│   Electron              │  데스크톱 애플리케이션
│   (윈도우 앱)           │
│   ┌─────────────────┐  │
│   │   Next.js       │  │  프론트엔드 (로컬)
│   │   (Frontend)    │  │  - 사용자 인터페이스
│   │                 │  │  - React 컴포넌트
│   └────────┬────────┘  │
└────────────┼────────────┘
             │ HTTP/REST API (로컬)
             │
┌────────────▼────────┐
│  FastAPI           │  백엔드 API (포트: 8000)
│  (Backend API)     │  - 비즈니스 로직
│                    │  - 데이터베이스 관리
│                    │  - CRUD 작업
└────────────┬───────┘
             │
             │ SQLAlchemy
             │
┌────────────▼────────┐
│    SQLite           │  데이터베이스
│  (accountbook.db)   │  - 거래 내역 저장
└─────────────────────┘

┌─────────────────────┐
│   FastAPI           │  AI 서비스 (포트: 8001)
│  (AI Service)       │  - 카테고리 분류
│                     │  - 자연어 처리
│                     │  - 패턴 분석
│                     │  - 예측 모델
└─────────────────────┘
         ▲
         │ HTTP API 호출
         │
┌────────┴────────────┐
│  FastAPI            │  필요 시 AI 서비스 호출
│  (Backend API)      │  (HTTP 클라이언트 사용)
└─────────────────────┘
```

**배포 모드**:
- **데스크톱 앱**: Electron이 Next.js를 번들링하여 독립 실행형 윈도우 앱으로 패키징
- **백엔드 서비스**: FastAPI 서비스들이 로컬에서 실행 (또는 별도 서버)

### 서비스 간 통신
- **Next.js → FastAPI Backend API**: REST API 호출 (거래 CRUD, 통계 등)
- **FastAPI Backend API → FastAPI AI Service**: AI 기능 요청 (카테고리 분류, 자연어 처리 등)
- **FastAPI Backend API → SQLite**: 데이터베이스 CRUD 작업 (SQLAlchemy)

### 마이크로서비스 장점
- **독립적 배포**: 각 서비스를 독립적으로 배포 및 확장 가능
- **기술 스택 통일**: Python 기반으로 통일되어 개발 효율성 향상
- **명확한 책임 분리**: 백엔드 API와 AI 서비스의 역할이 명확히 분리
- **확장성**: AI 서비스만 별도로 스케일링 가능 (예: GPU 서버에 AI 서비스만 배포)
- **유지보수 용이**: 각 서비스가 독립적이어서 버그 수정 및 업데이트가 용이

### FastAPI 선택 이유
- **높은 성능**: Node.js 및 Go와 유사한 성능 (비동기 지원)
- **자동 API 문서화**: Swagger UI 자동 생성 (`/docs` 엔드포인트)
- **타입 안정성**: Pydantic을 통한 런타임 타입 검증
- **Python 생태계**: AI/ML 라이브러리와의 쉬운 통합
- **빠른 개발**: 간단한 문법으로 빠른 프로토타이핑 가능

### Electron + Next.js 선택 이유
- **웹 기술 활용**: React/Next.js의 풍부한 생태계 활용
- **크로스 플랫폼**: 동일한 코드로 Windows, macOS, Linux 지원 가능
- **네이티브 기능**: 파일 시스템, 시스템 알림 등 네이티브 기능 접근
- **오프라인 지원**: 로컬 서비스와 함께 완전한 오프라인 동작 가능
- **빠른 개발**: 웹 개발 경험을 그대로 활용

## 개발 환경 설정

### 필수 요구사항
- Node.js 18+
- Python 3.10+
- SQLite (Python에서 자동 지원, 별도 설치 불필요)

### 설치 및 실행

#### 1. 프론트엔드 (Next.js + Electron)

**개발 모드 (웹)**:
```powershell
cd ./frontend
npm install
npm run dev          # Next.js 개발 서버 (http://localhost:3000)
```

**개발 모드 (Electron 앱)**:
```powershell
cd ./frontend
npm run dev:electron # Next.js + Electron 개발 모드
```

**프로덕션 빌드**:
```powershell
cd ./frontend
npm run build        # Next.js 프로덕션 빌드
npm run build:electron  # Electron 윈도우 앱 빌드 (.exe 파일 생성)
```

**빌드 결과물**:
- `frontend/dist/`: Electron 앱 실행 파일
- `frontend/dist/*.exe`: 윈도우 설치 파일

#### 2. 백엔드 API (FastAPI)
```powershell
cd ./backend-api
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
# 또는
uvicorn app.main:app --reload --port 8000
```

#### 3. AI 서비스 (FastAPI)
```powershell
cd ./ai-service
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8001
# 또는
uvicorn app.main:app --reload --port 8001
```

**참고**: 
- FastAPI 백엔드 API: `http://localhost:8000`
- FastAPI AI 서비스: `http://localhost:8001`
- Next.js 프론트엔드: `http://localhost:3000`

**동시 실행 (PowerShell에서 별도 터미널)**:
```powershell
# 터미널 1: 백엔드 API
cd ./backend-api; uvicorn app.main:app --reload --port 8000

# 터미널 2: AI 서비스
cd ./ai-service; uvicorn app.main:app --reload --port 8001

# 터미널 3: 프론트엔드
cd ./frontend; npm run dev
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
- [ ] Electron 앱 최적화
- [ ] 윈도우 설치 파일 패키징 (.exe)
- [ ] 자동 업데이트 기능 (Electron Updater)
- [ ] 웹 배포 (선택사항: Vercel, AWS 등)

## Electron 윈도우 앱 빌드 가이드

### 빌드 전 준비사항

1. **Next.js 프로덕션 빌드**: Next.js 앱을 먼저 빌드해야 합니다.
2. **Electron Builder 설정**: `electron-builder.json` 파일에서 빌드 옵션 설정
3. **아이콘 준비**: 윈도우 앱 아이콘 파일 (`.ico` 형식)

### 빌드 스크립트 예시

`frontend/package.json`에 다음 스크립트를 추가:

```json
{
  "scripts": {
    "dev": "next dev",
    "dev:electron": "concurrently \"next dev\" \"wait-on http://localhost:3000 && electron .\"",
    "build": "next build",
    "build:electron": "next build && electron-builder",
    "dist": "npm run build && electron-builder"
  }
}
```

### Electron Builder 설정 예시

`frontend/electron-builder.json`:

```json
{
  "appId": "com.accountbook.app",
  "productName": "AI 가계부",
  "directories": {
    "output": "dist"
  },
  "files": [
    "out/**/*",
    "electron/**/*",
    "package.json"
  ],
  "win": {
    "target": [
      {
        "target": "nsis",
        "arch": ["x64"]
      }
    ],
    "icon": "build/icon.ico"
  },
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true
  }
}
```

### 빌드 실행

```powershell
cd ./frontend
npm run build:electron
```

빌드 완료 후 `frontend/dist/` 폴더에 `.exe` 설치 파일이 생성됩니다.

### 주의사항

- **백엔드 서비스 포함**: Electron 앱에 FastAPI 서비스를 함께 번들링하려면 추가 설정이 필요합니다.
- **대안**: 백엔드 서비스를 별도로 실행하거나, Electron 앱 시작 시 자동으로 백엔드 서비스를 실행하도록 설정할 수 있습니다.
- **파일 크기**: Electron 앱은 상대적으로 큰 파일 크기를 가질 수 있습니다 (약 100-200MB).

## 라이선스

MIT License
