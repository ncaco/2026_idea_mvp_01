from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routers import transactions, categories, statistics, auth, budgets, ai, reports

# 환경 변수 로드
load_dotenv()

app = FastAPI(title="가계부 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])


@app.get("/")
async def root():
    return {"message": "가계부 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
