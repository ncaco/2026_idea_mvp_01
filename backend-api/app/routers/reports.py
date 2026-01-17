"""
리포트 생성 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.services import report_service
import json

router = APIRouter()


@router.get("/monthly")
def get_monthly_report(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    format: str = Query("json", regex="^(json|pdf)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """월별 리포트 생성"""
    report_data = report_service.generate_monthly_report(
        db=db,
        user_id=current_user.id,
        year=year,
        month=month
    )
    
    if format == "pdf":
        # PDF 생성은 나중에 구현 (ReportLab, WeasyPrint 등 사용)
        # 현재는 JSON 반환
        return Response(
            content=json.dumps(report_data, ensure_ascii=False, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=리포트_{year}_{month:02d}.json"
            }
        )
    else:
        return report_data
