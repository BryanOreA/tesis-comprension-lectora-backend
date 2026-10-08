from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User
from app.models.progress import Progress

router = APIRouter(prefix="/students", tags=["Estudiantes"])


@router.get("/{student_id}/progress")
def get_student_progress(student_id: int, db: Session = Depends(get_db)):
    progress = db.query(Progress).filter(Progress.student_id == student_id).order_by(Progress.created_at).all()
    if not progress:
        return {
            "student_id": student_id,
            "sessions": 0,
            "averageScore": 0,
            "currentLevel": "En Inicio",
            "points": 0,
            "evolution": []
        }

    total_score = sum(p.score for p in progress)
    total_questions = sum(p.total_questions for p in progress)
    avg = (total_score / total_questions * 100) if total_questions else 0

    # Evolución para gráfico
    evolution = [
        {
            "date": p.created_at.strftime("%Y-%m-%d"),
            "score": round((p.score / p.total_questions * 100) if p.total_questions else 0, 1),
            "level": p.level
        }
        for p in progress
    ]

    return {
        "student_id": student_id,
        "sessions": len(progress),
        "averageScore": round(avg, 1),
        "currentLevel": progress[-1].level,
        "points": sum(p.points_earned for p in progress),
        "evolution": evolution
    }


@router.get("/{student_id}/detail")
def get_student_detail(student_id: int, db: Session = Depends(get_db)):
    """Detalle completo de un estudiante incluyendo alertas."""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    progress = db.query(Progress).filter(Progress.student_id == student_id).order_by(Progress.created_at).all()

    if not progress:
        return {
            "id": student.id,
            "name": student.full_name,
            "username": student.username,
            "level": "En Inicio",
            "averageScore": 0,
            "totalSessions": 0,
            "totalPoints": 0,
            "alerts": [{"type": "info", "message": "Aún no ha realizado ninguna lectura"}],
            "evolution": []
        }

    total_score = sum(p.score for p in progress)
    total_q = sum(p.total_questions for p in progress)
    avg = (total_score / total_q * 100) if total_q else 0

    # Generar alertas inteligentes
    alerts = []
    last_session = progress[-1].created_at
    days_since_last = (datetime.utcnow() - last_session).days

    # Alerta 1: Sin actividad reciente
    if days_since_last > 3:
        alerts.append({
            "type": "warning",
            "message": f"Sin actividad desde hace {days_since_last} días",
            "icon": "clock"
        })

    # Alerta 2: Nivel estancado
    last_3 = progress[-3:] if len(progress) >= 3 else progress
    if len(last_3) >= 3 and all(p.level == "En Inicio" for p in last_3):
        alerts.append({
            "type": "danger",
            "message": "Lleva 3 sesiones consecutivas en nivel 'En Inicio'",
            "icon": "alert-triangle"
        })

    # Alerta 3: Caída de puntaje
    if len(progress) >= 2:
        last_score = (progress[-1].score / progress[-1].total_questions * 100) if progress[-1].total_questions else 0
        prev_score = (progress[-2].score / progress[-2].total_questions * 100) if progress[-2].total_questions else 0
        if prev_score - last_score > 30:
            alerts.append({
                "type": "danger",
                "message": f"Caída de {round(prev_score - last_score)}% respecto a la sesión anterior",
                "icon": "trending-down"
            })

    # Alerta 4: Buen desempeño
    if avg >= 80 and len(progress) >= 3:
        alerts.append({
            "type": "success",
            "message": "¡Excelente desempeño sostenido!",
            "icon": "trending-up"
        })

    evolution = [
        {
            "date": p.created_at.strftime("%Y-%m-%d"),
            "score": round((p.score / p.total_questions * 100) if p.total_questions else 0, 1),
            "level": p.level
        }
        for p in progress
    ]

    return {
        "id": student.id,
        "name": student.full_name,
        "username": student.username,
        "level": progress[-1].level,
        "averageScore": round(avg, 1),
        "totalSessions": len(progress),
        "totalPoints": sum(p.points_earned for p in progress),
        "alerts": alerts,
        "evolution": evolution
    }


@router.get("/all")
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(User).filter(User.role == "estudiante").all()
    result = []

    for s in students:
        progress = db.query(Progress).filter(Progress.student_id == s.id).order_by(Progress.created_at).all()
        total_score = sum(p.score for p in progress)
        total_q = sum(p.total_questions for p in progress)
        avg = round((total_score / total_q * 100) if total_q else 0)

        # Determinar si necesita alerta
        needs_alert = False
        if not progress:
            needs_alert = True
        elif (datetime.utcnow() - progress[-1].created_at).days > 3:
            needs_alert = True
        elif avg < 50:
            needs_alert = True

        last_session = "Nunca"
        if progress:
            days = (datetime.utcnow() - progress[-1].created_at).days
            if days == 0:
                last_session = "Hoy"
            elif days == 1:
                last_session = "Ayer"
            else:
                last_session = f"Hace {days} días"

        result.append({
            "id": s.id,
            "name": s.full_name,
            "username": s.username,
            "level": progress[-1].level if progress else "En Inicio",
            "progress": avg,
            "totalSessions": len(progress),
            "needsAlert": needs_alert,
            "lastSession": last_session
        })

    return result