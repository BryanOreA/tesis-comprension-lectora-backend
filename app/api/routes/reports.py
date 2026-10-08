from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import csv
import io
from app.db.database import get_db
from app.models.user import User
from app.models.progress import Progress

router = APIRouter(prefix="/reports", tags=["Reportes"])

# BOM UTF-8 para que Excel reconozca correctamente los caracteres
UTF8_BOM = '\ufeff'


@router.get("/student/{student_id}/csv")
def export_student_csv(student_id: int, db: Session = Depends(get_db)):
    """Exporta el progreso de un estudiante en formato CSV."""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    progress = db.query(Progress).filter(Progress.student_id == student_id).order_by(Progress.created_at).all()

    output = io.StringIO()
    output.write(UTF8_BOM)  # ← BOM UTF-8
    writer = csv.writer(output)
    writer.writerow(["Fecha", "Texto ID", "Aciertos", "Total", "Tiempo (s)", "Nivel", "Puntos"])

    for p in progress:
        writer.writerow([
            p.created_at.strftime("%Y-%m-%d %H:%M"),
            p.text_id,
            p.score,
            p.total_questions,
            round(p.time_spent, 1),
            p.level,
            p.points_earned
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=reporte_{student.username}_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


@router.get("/class/csv")
def export_class_csv(db: Session = Depends(get_db)):
    """Exporta el progreso de toda la clase en formato CSV."""
    students = db.query(User).filter(User.role == "estudiante").all()

    output = io.StringIO()
    output.write(UTF8_BOM)  # ← BOM UTF-8
    writer = csv.writer(output)
    writer.writerow(["Estudiante", "Nivel Actual", "Promedio", "Textos Leídos", "Última Sesión"])

    for student in students:
        progress = db.query(Progress).filter(Progress.student_id == student.id).all()
        total_score = sum(p.score for p in progress)
        total_q = sum(p.total_questions for p in progress)
        avg = round((total_score / total_q * 100) if total_q else 0)

        last = progress[-1].created_at.strftime("%Y-%m-%d") if progress else "Nunca"

        writer.writerow([
            student.full_name,
            progress[-1].level if progress else "En Inicio",
            f"{avg}%",
            len(progress),
            last
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=reporte_clase_{datetime.now().strftime('%Y%m%d')}.csv"}
    )