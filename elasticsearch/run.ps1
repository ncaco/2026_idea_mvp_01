# 엘라스틱서치 실행 스크립트

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "status", "init")]
    [string]$Action = "start"
)

$ErrorActionPreference = "Stop"

function Start-Elasticsearch {
    Write-Host "엘라스틱서치 시작 중..." -ForegroundColor Green
    docker-compose up -d elasticsearch
    
    Write-Host "엘라스틱서치가 시작될 때까지 대기 중..." -ForegroundColor Yellow
    $maxRetries = 30
    $retryCount = 0
    
    while ($retryCount -lt $maxRetries) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:9200" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "엘라스틱서치가 준비되었습니다!" -ForegroundColor Green
                return $true
            }
        } catch {
            $retryCount++
            Start-Sleep -Seconds 2
            Write-Host "." -NoNewline
        }
    }
    
    Write-Host "`n엘라스틱서치 시작 시간 초과" -ForegroundColor Red
    return $false
}

function Stop-Elasticsearch {
    Write-Host "엘라스틱서치 중지 중..." -ForegroundColor Yellow
    docker-compose stop elasticsearch kibana
    Write-Host "엘라스틱서치가 중지되었습니다." -ForegroundColor Green
}

function Get-ElasticsearchStatus {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9200" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "엘라스틱서치가 실행 중입니다." -ForegroundColor Green
            $clusterInfo = Invoke-RestMethod -Uri "http://localhost:9200" -Method Get
            Write-Host "클러스터: $($clusterInfo.cluster_name)" -ForegroundColor Cyan
            Write-Host "버전: $($clusterInfo.version.number)" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "엘라스틱서치가 실행 중이지 않습니다." -ForegroundColor Red
    }
}

function Initialize-Index {
    Write-Host "인덱스 초기화 중..." -ForegroundColor Green
    
    # Python 가상 환경 활성화
    $venvPath = Join-Path $PSScriptRoot "..\backend-api\venv"
    if (Test-Path $venvPath) {
        & "$venvPath\Scripts\Activate.ps1"
    }
    
    # 인덱스 초기화 스크립트 실행
    $scriptPath = Join-Path $PSScriptRoot "init-index.py"
    python $scriptPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "인덱스 초기화 완료!" -ForegroundColor Green
    } else {
        Write-Host "인덱스 초기화 실패!" -ForegroundColor Red
    }
}

switch ($Action) {
    "start" {
        Start-Elasticsearch
    }
    "stop" {
        Stop-Elasticsearch
    }
    "restart" {
        Stop-Elasticsearch
        Start-Sleep -Seconds 2
        Start-Elasticsearch
    }
    "status" {
        Get-ElasticsearchStatus
    }
    "init" {
        if (Start-Elasticsearch) {
            Start-Sleep -Seconds 3
            Initialize-Index
        }
    }
}
