# Backend API 실행 스크립트
# PowerShell 스크립트

Write-Host "Backend API 시작 중..." -ForegroundColor Green

# backend-api 디렉토리로 이동
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 가상환경 확인 및 생성
if (-not (Test-Path "venv")) {
    Write-Host "가상환경 생성 중..." -ForegroundColor Yellow
    python -m venv venv
}

# 가상환경 활성화
Write-Host "가상환경 활성화 중..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# 의존성 설치
Write-Host "의존성 설치 중..." -ForegroundColor Yellow
pip install -r requirements.txt

# 데이터베이스 초기화 (선택적)
Write-Host "데이터베이스 초기화 중..." -ForegroundColor Yellow
python -m app.init_db

# FastAPI 서버 실행
Write-Host "FastAPI 서버 시작 중..." -ForegroundColor Green
Write-Host "서버 주소: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API 문서: http://localhost:8000/docs" -ForegroundColor Cyan

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
