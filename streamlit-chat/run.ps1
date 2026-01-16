# Streamlit Chat 실행 스크립트
# PowerShell 스크립트

Write-Host "Streamlit Chat 시작 중..." -ForegroundColor Green

# streamlit-chat 디렉토리로 이동
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

# Streamlit 앱 실행
Write-Host "Streamlit 앱 시작 중..." -ForegroundColor Green
Write-Host "서버 주소: http://localhost:8501" -ForegroundColor Cyan

streamlit run app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false
