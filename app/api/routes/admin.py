from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional
from app.db.database import get_db
from app.models.user import User
from app.models.progress import Progress
from app.models.text import Text

router = APIRouter(prefix="/admin", tags=["Administración"])


def require_admin(admin_id: int, db: Session):
    """Verifica que el usuario sea administrador."""
    admin = db.query(User).filter(User.id == admin_id).first()
    if not admin or admin.role != "administrador":
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere rol administrador")
    return admin


# ============================
# ESTADÍSTICAS GLOBALES
# ============================
@router.get("/stats")
def get_global_stats(admin_id: int = 1, db: Session = Depends(get_db)):
    """Estadísticas globales del sistema."""
    require_admin(admin_id, db)

    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == "estudiante").count()
    total_teachers = db.query(User).filter(User.role == "docente").count()
    total_parents = db.query(User).filter(User.role == "padre").count()
    total_admins = db.query(User).filter(User.role == "administrador").count()

    total_sessions = db.query(Progress).count()
    total_texts = db.query(Text).count()

    # Sesiones en los últimos 7 días
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    recent_sessions = db.query(Progress).filter(Progress.created_at >= one_week_ago).count()

    # Sesiones de hoy
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = db.query(Progress).filter(Progress.created_at >= today_start).count()

    # Promedio general
    total_score = db.query(func.sum(Progress.score)).scalar() or 0
    total_questions = db.query(func.sum(Progress.total_questions)).scalar() or 0
    avg_score = round((total_score / total_questions * 100) if total_questions else 0, 1)

    # Distribución de niveles
    level_distribution = db.query(
        Progress.level, func.count(Progress.id)
    ).group_by(Progress.level).all()

    levels = {"En Inicio": 0, "En Proceso": 0, "Satisfactorio": 0}
    for level, count in level_distribution:
        if level in levels:
            levels[level] = count

    return {
        "users": {
            "total": total_users,
            "students": total_students,
            "teachers": total_teachers,
            "parents": total_parents,
            "admins": total_admins
        },
        "content": {
            "totalTexts": total_texts,
            "totalSessions": total_sessions
        },
        "activity": {
            "recentSessions": recent_sessions,
            "todaySessions": today_sessions,
            "averageScore": avg_score
        },
        "levelDistribution": levels
    }


# ============================
# LISTA DE USUARIOS
# ============================
@router.get("/users")
def get_all_users(
    admin_id: int = 1,
    role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos los usuarios con filtros opcionales."""
    require_admin(admin_id, db)

    query = db.query(User)

    if role and role != "todos":
        query = query.filter(User.role == role)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_term)) |
            (User.username.ilike(search_term)) |
            (User.email.ilike(search_term))
        )

    users = query.order_by(desc(User.created_at)).all()

    result = []
    for user in users:
        # Contar sesiones si es estudiante
        sessions = 0
        if user.role == "estudiante":
            sessions = db.query(Progress).filter(Progress.student_id == user.id).count()

        result.append({
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.strftime("%Y-%m-%d"),
            "sessions": sessions
        })

    return result


# ============================
# DETALLE DE USUARIO
# ============================
@router.get("/users/{user_id}")
def get_user_detail(user_id: int, admin_id: int = 1, db: Session = Depends(get_db)):
    """Detalle completo de un usuario."""
    require_admin(admin_id, db)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    detail = {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.strftime("%Y-%m-%d"),
    }

    # Si es estudiante, agregar estadísticas
    if user.role == "estudiante":
        progress = db.query(Progress).filter(Progress.student_id == user.id).all()
        total_score = sum(p.score for p in progress)
        total_q = sum(p.total_questions for p in progress)
        avg = round((total_score / total_q * 100) if total_q else 0, 1)

        detail["stats"] = {
            "totalSessions": len(progress),
            "averageScore": avg,
            "currentLevel": progress[-1].level if progress else "En Inicio",
            "totalPoints": sum(p.points_earned for p in progress)
        }

        detail["evolution"] = [
            {
                "date": p.created_at.strftime("%Y-%m-%d"),
                "score": round((p.score / p.total_questions * 100) if p.total_questions else 0, 1),
                "level": p.level
            }
            for p in progress
        ]

    return detail


# ============================
# ACTIVAR/DESACTIVAR USUARIO
# ============================
@router.put("/users/{user_id}/toggle")
def toggle_user_status(user_id: int, admin_id: int = 1, db: Session = Depends(get_db)):
    """Activa o desactiva un usuario."""
    require_admin(admin_id, db)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.id == admin_id:
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")

    user.is_active = not user.is_active
    db.commit()

    return {
        "id": user.id,
        "is_active": user.is_active,
        "message": f"Usuario {'activado' if user.is_active else 'desactivado'} correctamente"
    }