from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.notion_sync import sync_tasks_from_notion

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/notion")
async def trigger_notion_sync(db: Session = Depends(get_db)):
    result = await sync_tasks_from_notion(db)
    return {"status": "ok", "created": result["created"], "updated": result["updated"]}
