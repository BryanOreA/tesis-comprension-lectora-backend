from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Dict
import json
from app.db.database import get_db
from app.models.progress import SyncEvent

router = APIRouter(prefix="/sync", tags=["Sincronización"])


class SyncPayload(BaseModel):
    type: str
    textId: int | None = None
    answers: list = []
    studentId: int | None = None


@router.post("/")
def sync_event(payload: SyncPayload, db: Session = Depends(get_db)):
    event = SyncEvent(
        student_id=payload.studentId or 1,
        event_type=payload.type,
        payload=json.dumps(payload.dict()),
        synced=1
    )
    db.add(event)
    db.commit()
    return {"status": "ok", "received": payload.type}