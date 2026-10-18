from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Dict, List
import json
from app.db.database import get_db
from app.models.progress import SyncEvent, Progress
from app.models.quiz import Quiz
from app.services.ml_service import classify_level

router = APIRouter(prefix="/sync", tags=["Sincronización"])


class SyncPayload(BaseModel):
    type: str
    textId: int | None = None
    answers: List[dict] = []
    studentId: int | None = None


@router.post("/")
def sync_event(payload: SyncPayload, db: Session = Depends(get_db)):
    """
    Recibe eventos offline, los registra y si es un quiz, lo califica.
    """
    student_id = payload.studentId or 1
    
    # Si el evento es un quiz offline, procesarlo igual que en línea
    if payload.type == 'quiz_submit' and payload.textId:
        questions = db.query(Quiz).filter(Quiz.text_id == payload.textId).all()
        
        if questions:
            correct_count = 0
            total_time = 0.0
            
            for answer in payload.answers:
                # Aquí asumimos que 'answer' viene como el texto seleccionado
                q = next((q for q in questions if q.id == answer.get('questionId')), None)
                if q:
                    options = [q.option_a, q.option_b, q.option_c, q.option_d]
                    correct_text = options[q.correct_answer]
                    
                    if str(correct_text).strip().lower() == str(answer.get('answer')).strip().lower():
                        correct_count += 1
                total_time += answer.get('timeSpent', 0.0)
            
            total = len(questions)
            percentage = (correct_count / total) * 100 if total else 0
            avg_time = total_time / max(len(payload.answers), 1)
            
            new_level = classify_level(
                percentage=percentage,
                avg_time=avg_time,
                attempts=len(payload.answers),
                help_used=0
            )
            
            # Registrar el progreso en la base de datos central
            progress = Progress(
                student_id=student_id,
                text_id=payload.textId,
                score=correct_count,
                total_questions=total,
                time_spent=total_time,
                level=new_level,
                points_earned=correct_count * 10
            )
            db.add(progress)

    # Guardar el log del evento por auditoría
    event = SyncEvent(
        student_id=student_id,
        event_type=payload.type,
        payload=json.dumps(payload.dict()),
        synced=1
    )
    db.add(event)
    db.commit()
    
    return {"status": "ok", "received": payload.type, "student_id": student_id}