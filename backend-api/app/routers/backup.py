from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import json
import io
from app.database import get_db
from app.core.security import get_current_user
from app.models import User, Transaction, Category, Budget, RecurringTransaction, Tag
from app.services import transaction_service, category_service, budget_service, recurring_transaction_service, tag_service

router = APIRouter()


@router.get("/export")
def export_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """데이터 백업 (JSON 형식)"""
    try:
        # 모든 데이터 조회
        transactions = transaction_service.get_transactions(db, current_user.id, skip=0, limit=100000)
        categories = category_service.get_categories(db, current_user.id)
        budgets = budget_service.get_budgets(db, current_user.id)
        
        # 반복 거래 조회
        from app.services import recurring_transaction_service
        recurring = recurring_transaction_service.get_recurring_transactions(db, current_user.id)
        
        # 태그 조회
        from app.services import tag_service
        tags = tag_service.get_tags(db, current_user.id)
        
        # JSON 데이터 구성
        backup_data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'user_id': current_user.id,
            'username': current_user.username,
            'data': {
                'categories': [
                    {
                        'name': c.name,
                        'type': c.type,
                        'color': c.color,
                        'icon': c.icon,
                    }
                    for c in categories
                ],
                'transactions': [
                    {
                        'category_id': t.category_id,
                        'type': t.type,
                        'amount': float(t.amount),
                        'description': t.description,
                        'transaction_date': t.transaction_date.isoformat(),
                        'tags': [{'name': tag.name} for tag in t.tags] if hasattr(t, 'tags') and t.tags else []
                    }
                    for t in transactions
                ],
                'budgets': [
                    {
                        'category_id': b.category_id,
                        'amount': float(b.amount),
                        'month': b.month,
                    }
                    for b in budgets
                ],
                'recurring_transactions': [
                    {
                        'category_id': r.category_id,
                        'type': r.type,
                        'amount': float(r.amount),
                        'description': r.description,
                        'frequency': r.frequency,
                        'day_of_month': r.day_of_month,
                        'day_of_week': r.day_of_week,
                        'start_date': r.start_date.isoformat(),
                        'end_date': r.end_date.isoformat() if r.end_date else None,
                        'is_active': r.is_active,
                    }
                    for r in recurring
                ],
                'tags': [
                    {
                        'name': t.name,
                        'color': t.color,
                    }
                    for t in tags
                ],
            }
        }
        
        # JSON 파일 생성
        json_str = json.dumps(backup_data, ensure_ascii=False, indent=2)
        json_bytes = json_str.encode('utf-8')
        
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return StreamingResponse(
            io.BytesIO(json_bytes),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"백업 실패: {str(e)}")


@router.post("/import")
async def import_data(
    file_content: str = Body(..., media_type="application/json"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """데이터 복원 (JSON 형식)"""
    try:
        # JSON 파싱
        data = json.loads(file_content) if isinstance(file_content, str) else file_content
        
        if 'data' not in data:
            raise HTTPException(status_code=400, detail="잘못된 백업 파일 형식입니다.")
        
        imported = {
            'categories': 0,
            'transactions': 0,
            'budgets': 0,
            'recurring_transactions': 0,
            'tags': 0,
        }
        
        # 카테고리 복원
        if 'categories' in data['data']:
            existing_categories = {c.name: c for c in category_service.get_categories(db, current_user.id)}
            for cat_data in data['data']['categories']:
                try:
                    if cat_data['name'] not in existing_categories:
                        from app.schemas.category import CategoryCreate
                        category_service.create_category(
                            db,
                            CategoryCreate(**cat_data),
                            current_user.id
                        )
                        imported['categories'] += 1
                except Exception:
                    pass  # 중복 카테고리 무시
        
        # 태그 복원
        if 'tags' in data['data']:
            existing_tags = {t.name: t for t in tag_service.get_tags(db, current_user.id)}
            for tag_data in data['data']['tags']:
                try:
                    if tag_data['name'] not in existing_tags:
                        from app.schemas.tag import TagCreate
                        tag_service.create_tag(
                            db,
                            TagCreate(**tag_data),
                            current_user.id
                        )
                        imported['tags'] += 1
                except Exception:
                    pass
        
        # 거래 복원
        if 'transactions' in data['data']:
            categories = {c.id: c.id for c in category_service.get_categories(db, current_user.id)}
            tags = {t.name: t.id for t in tag_service.get_tags(db, current_user.id)}
            
            for trans_data in data['data']['transactions']:
                try:
                    category_id = trans_data.get('category_id')
                    if not category_id or category_id not in categories:
                        continue
                    
                    tag_ids = []
                    if 'tags' in trans_data:
                        for tag_info in trans_data['tags']:
                            tag_name = tag_info.get('name') if isinstance(tag_info, dict) else tag_info
                            if tag_name in tags:
                                tag_ids.append(tags[tag_name])
                    
                    from app.schemas.transaction import TransactionCreate
                    trans_create = TransactionCreate(
                        category_id=category_id,
                        type=trans_data['type'],
                        amount=trans_data['amount'],
                        description=trans_data.get('description'),
                        transaction_date=trans_data['transaction_date'],
                        tag_ids=tag_ids if tag_ids else None
                    )
                    transaction_service.create_transaction(db, trans_create, current_user.id)
                    imported['transactions'] += 1
                except Exception as e:
                    print(f"거래 복원 오류: {e}")
                    pass
        
        # 예산 복원
        if 'budgets' in data['data']:
            for budget_data in data['data']['budgets']:
                try:
                    from app.schemas.budget import BudgetCreate
                    budget_service.create_budget(
                        db,
                        BudgetCreate(**budget_data),
                        current_user.id
                    )
                    imported['budgets'] += 1
                except Exception:
                    pass
        
        # 반복 거래 복원
        if 'recurring_transactions' in data['data']:
            for rec_data in data['data']['recurring_transactions']:
                try:
                    from app.schemas.recurring_transaction import RecurringTransactionCreate
                    recurring_transaction_service.create_recurring_transaction(
                        db,
                        current_user.id,
                        RecurringTransactionCreate(**rec_data)
                    )
                    imported['recurring_transactions'] += 1
                except Exception:
                    pass
        
        return JSONResponse({
            'message': '데이터 복원이 완료되었습니다.',
            'imported': imported
        })
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="잘못된 JSON 파일입니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"복원 실패: {str(e)}")
