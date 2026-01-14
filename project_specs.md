# 프로젝트 명세 및 작업 추적

## 프로젝트 정보
- **프로젝트명**: AI 가계부 - 웹 애플리케이션
- **시작일**: 2026-01
- **목표**: AI 기능이 포함된 웹 기반 가계부 애플리케이션 개발

## 기술 스택
- **프론트엔드**: Next.js + Electron + TypeScript + Tailwind CSS
- **백엔드 API**: FastAPI + SQLite + SQLAlchemy (마이크로서비스)
- **AI 서비스**: FastAPI + OpenAI API / Local LLM (마이크로서비스)

## 작업 추적

### Phase 1: 기본 기능 (MVP) - 진행 중

#### 1.1 프로젝트 구조 설정
- [ ] 프론트엔드 프로젝트 초기화 (Next.js + Electron + TypeScript)
- [ ] Electron 메인 프로세스 설정
- [ ] Electron Preload 스크립트 설정
- [ ] 백엔드 API 프로젝트 초기화 (FastAPI)
- [ ] AI 서비스 프로젝트 초기화 (FastAPI)
- [ ] 프로젝트 루트 구조 설정
- [ ] Git 저장소 초기화 및 .gitignore 설정
- [ ] CORS 설정 (Next.js ↔ FastAPI Backend ↔ FastAPI AI)

#### 1.2 데이터베이스 스키마 설계
- [ ] 데이터베이스 스키마 설계 완료 (db_structure.md)
- [ ] SQLite 데이터베이스 파일 생성
- [ ] SQLAlchemy 모델 클래스 작성
- [ ] Pydantic 스키마 작성
- [ ] 데이터베이스 초기화 및 마이그레이션
- [ ] 초기 데이터 (기본 카테고리) 삽입

#### 1.3 기본 CRUD 기능
- [ ] Transaction SQLAlchemy 모델 작성
- [ ] Transaction Pydantic 스키마 작성
- [ ] Transaction Service 구현
- [ ] Transaction Router (REST API) 구현
- [ ] Category SQLAlchemy 모델 작성
- [ ] Category Service 및 Router 구현
- [ ] 프론트엔드 거래 내역 등록 폼
- [ ] 프론트엔드 거래 내역 목록 조회
- [ ] 프론트엔드 거래 내역 수정/삭제

#### 1.4 카테고리 관리
- [ ] 카테고리 목록 조회 API
- [ ] 카테고리 추가/수정/삭제 API
- [ ] 프론트엔드 카테고리 관리 UI
- [ ] 카테고리 선택 드롭다운/모달

#### 1.5 기본 통계 및 차트
- [ ] 월별 수입/지출 합계 API
- [ ] 카테고리별 지출 통계 API
- [ ] 프론트엔드 대시보드 UI
- [ ] 차트 라이브러리 연동 (Chart.js/Recharts)
- [ ] 월별 수입/지출 차트
- [ ] 카테고리별 지출 파이 차트

### Phase 2: AI 기능 추가

#### 2.1 AI 서비스 구축
- [ ] FastAPI AI 서비스 프로젝트 설정
- [ ] OpenAI API 연동 또는 Local LLM 설정
- [ ] AI 서비스 엔드포인트 구현
- [ ] 백엔드 API에서 AI 서비스 HTTP 클라이언트 구현
- [ ] 서비스 간 통신 테스트

#### 2.2 자동 카테고리 분류
- [ ] 거래 설명 분석 API
- [ ] 카테고리 추천 로직
- [ ] 프론트엔드에서 자동 카테고리 제안 UI
- [ ] 사용자 피드백 수집 (추천 수락/거부)

#### 2.3 자연어 입력 처리
- [ ] 자연어 파싱 API
- [ ] 날짜, 금액, 카테고리 추출
- [ ] 프론트엔드 자연어 입력 필드
- [ ] 실시간 파싱 결과 미리보기

#### 2.4 지출 패턴 분석
- [ ] 지출 패턴 분석 API
- [ ] 월별/요일별/시간대별 패턴 분석
- [ ] 비정상 지출 감지
- [ ] 프론트엔드 패턴 분석 리포트 UI

### Phase 3: 고급 기능

#### 3.1 예산 관리 및 추천
- [ ] 예산 설정 API
- [ ] 예산 대비 지출 현황 API
- [ ] AI 기반 예산 추천 API
- [ ] 프론트엔드 예산 관리 UI
- [ ] 예산 초과 알림

#### 3.2 지출 예측
- [ ] 시계열 분석 모델 구현
- [ ] 다음 달 지출 예측 API
- [ ] 프론트엔드 예측 차트

#### 3.3 리포트 생성
- [ ] 월별 리포트 생성 API
- [ ] PDF 리포트 생성 기능
- [ ] 프론트엔드 리포트 다운로드

#### 3.4 데이터 내보내기/가져오기
- [ ] CSV 내보내기 기능
- [ ] CSV 가져오기 기능
- [ ] Excel 내보내기 기능

### Phase 4: 최적화 및 배포

#### 4.1 성능 최적화
- [ ] 데이터베이스 쿼리 최적화
- [ ] 프론트엔드 렌더링 최적화
- [ ] API 응답 시간 개선

#### 4.2 UI/UX 개선
- [ ] 반응형 디자인 개선
- [ ] 다크 모드 지원
- [ ] 애니메이션 및 전환 효과
- [ ] 접근성 개선

#### 4.3 Electron 앱 빌드 및 배포
- [ ] Electron Builder 설정
- [ ] 윈도우 아이콘 및 메타데이터 설정
- [ ] Next.js 프로덕션 빌드 통합
- [ ] 윈도우 설치 파일 빌드 테스트 (.exe)
- [ ] 자동 업데이트 기능 (electron-updater)
- [ ] 코드 서명 설정 (선택사항)

#### 4.4 웹 배포 (선택사항)
- [ ] 환경 변수 설정 (.env 파일)
- [ ] 프로덕션 빌드 테스트
- [ ] 프론트엔드 웹 배포 (Vercel, Netlify 등)
- [ ] 백엔드 배포 (AWS, Azure, Heroku 등)
- [ ] AI 서비스 배포 (AWS Lambda, Docker 등)
- [ ] 도메인 및 SSL 설정

## 우선순위

### 높음 (P0)
- Phase 1의 모든 작업 (MVP 완성)

### 중간 (P1)
- Phase 2의 AI 기능 (핵심 차별화 요소)

### 낮음 (P2)
- Phase 3의 고급 기능
- Phase 4의 최적화 및 배포

## 진행 상황

**현재 단계**: Phase 1 - 기본 기능 (MVP)
**완료율**: 5% (데이터베이스 스키마 설계 완료)

## 다음 작업

1. Next.js 프로젝트 초기화
2. FastAPI 백엔드 API 프로젝트 초기화
3. FastAPI AI 서비스 프로젝트 초기화
4. SQLite 데이터베이스 설정
5. SQLAlchemy 모델 클래스 작성
6. CORS 설정
7. 서비스 간 통신 설정

## 참고사항

- SQLite를 사용하므로 별도의 데이터베이스 서버 설치 불필요
- 데이터베이스 파일은 `data/accountbook.db`에 저장
- 개발 환경: Windows 11, PowerShell, Command
