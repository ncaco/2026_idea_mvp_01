# 백엔드 API

FastAPI 기반 백엔드 API 서비스입니다.

## 설치

```powershell
cd backend-api
pip install -r requirements.txt
```

## 데이터베이스 초기화

데이터베이스를 처음 설정할 때:

```powershell
cd backend-api
python -m app.init_db
```

이 명령은 다음을 수행합니다:
- SQLite 데이터베이스 파일 생성 (`../data/accountbook.db`)
- 테이블 생성
- 기본 사용자 생성
- 기본 카테고리 생성

## 실행

```powershell
cd backend-api
uvicorn app.main:app --reload --port 8000
```

API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.
