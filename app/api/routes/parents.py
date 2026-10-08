from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User
from app.models.progress import Progress

router = APIRouter(prefix="/parents", tags=["Padres"])


def generate_recommendations(level: str, avg_score: float, sessions: int, streak_days: int):
    """Genera recomendaciones personalizadas según el desempeño del estudiante."""
    recommendations = []

    if level == "En Inicio":
        recommendations.append("Dedica 10 minutos diarios a leer en voz alta con tu hijo.")
        recommendations.append("Hazle preguntas sencillas sobre lo que leyó para reforzar la comprensión.")
        recommendations.append("Empieza con textos cortos y aumenten gradualmente la dificultad.")
    elif level == "En Proceso":
        recommendations.append("Motívalo a hacer predicciones sobre lo que pasará en el texto antes de leer.")
        recommendations.append("Pídele que cuente la historia con sus propias palabras al terminar.")
        recommendations.append("Conversa sobre las emociones de los personajes para mejorar la comprensión inferencial.")
    else:
        recommendations.append("Anímalo a leer textos más largos y de diferentes géneros.")
        recommendations.append("Pídele que opine sobre lo que leyó y justifique sus puntos de vista.")
        recommendations.append("Sugiere leer artículos de interés para aplicar la comprensión en contextos reales.")

    if avg_score < 50:
        recommendations.append("Refuercen las áreas de dificultad revisando juntos las respuestas incorrectas.")
    elif avg_score > 85:
        recommendations.append("¡Felicidades! Su desempeño es destacado. Motívalo a seguir así.")

    if streak_days == 0:
        recommendations.append("Ayúdalo a establecer una rutina diaria de lectura.")
    elif streak_days >= 3:
        recommendations.append(f"¡Excelente! Llevan {streak_days} días seguidos. Mantengan la constancia.")

    if sessions < 5:
        recommendations.append("Aún son pocas sesiones. Anímalo a leer más seguido para notar mejoras.")

    return recommendations[:5]


@router.get("/summary")
def get_weekly_summary(parent_id: int = 1, db: Session = Depends(get_db)):
    """Resumen semanal para el padre de familia."""
    # Obtener el primer estudiante (simplificación del modelo padre-hijo)
    student = db.query(User).filter(User.role == "estudiante").first()
    if not student:
        return {"error": "No hay estudiantes registrados"}

    # Progreso de la última semana
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_progress = db.query(Progress).filter(
        Progress.student_id == student.id,
        Progress.created_at >= one_week_ago
    ).order_by(Progress.created_at).all()

    # Progreso total
    all_progress = db.query(Progress).filter(
        Progress.student_id == student.id
    ).order_by(Progress.created_at).all()

    total_score = sum(p.score for p in all_progress)
    total_q = sum(p.total_questions for p in all_progress)
    avg = round((total_score / total_q * 100) if total_q else 0, 1)

    # Calcular racha
    streak = 0
    if all_progress:
        last_date = all_progress[-1].created_at.date()
        today = datetime.utcnow().date()
        if (today - last_date).days <= 1:
            streak = 1
            for i in range(len(all_progress) - 2, -1, -1):
                prev = all_progress[i].created_at.date()
                curr = all_progress[i + 1].created_at.date()
                if (curr - prev).days == 1:
                    streak += 1
                else:
                    break

    # Progreso por día (últimos 7 días)
    weekly_by_day = []
    day_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    for i in range(6, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        day_progress = [p for p in weekly_progress if p.created_at.date() == day]
        if day_progress:
            day_score = sum(p.score for p in day_progress)
            day_total = sum(p.total_questions for p in day_progress)
            day_avg = round((day_score / day_total * 100) if day_total else 0, 1)
        else:
            day_avg = 0

        # Obtener label del día de la semana en español
        weekday = day.weekday()  # 0 = Lunes
        weekly_by_day.append({
            "date": day.strftime("%Y-%m-%d"),
            "label": day_labels[weekday],
            "score": day_avg,
            "sessions": len(day_progress)
        })

    recommendations = generate_recommendations(
        level=all_progress[-1].level if all_progress else "En Inicio",
        avg_score=avg,
        sessions=len(all_progress),
        streak_days=streak
    )

    return {
        "studentId": student.id,
        "studentName": student.full_name,
        "textsRead": len(all_progress),
        "averageScore": avg,
        "currentLevel": all_progress[-1].level if all_progress else "En Inicio",
        "currentStreak": streak,
        "weeklyProgress": weekly_by_day,
        "recommendations": recommendations,
        "weeklySessions": len(weekly_progress)
    }