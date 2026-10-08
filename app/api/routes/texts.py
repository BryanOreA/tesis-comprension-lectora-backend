from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.text import Text
from app.models.quiz import Quiz
from app.schemas.text import TextResponse, QuizItem
from app.services.nlp_service import simplify_text, calculate_readability

router = APIRouter(prefix="/texts", tags=["Textos"])


@router.get("/level/{level}", response_model=TextResponse)
def get_text_by_level(level: str, db: Session = Depends(get_db)):
    text = db.query(Text).filter(Text.level == level).first()
    if not text:
        raise HTTPException(status_code=404, detail=f"No hay textos para el nivel '{level}'")

    questions_db = db.query(Quiz).filter(Quiz.text_id == text.id).all()
    questions = [
        QuizItem(
            id=q.id,
            question=q.question,
            options=[q.option_a, q.option_b, q.option_c, q.option_d],
            correctAnswer=q.correct_answer
        )
        for q in questions_db
    ]

    content = simplify_text(text.content, target_level=level)

    return TextResponse(
        id=text.id,
        title=text.title,
        content=content,
        level=text.level,
        questions=questions
    )


@router.get("/{text_id}/simplified")
def get_simplified_text(text_id: int, db: Session = Depends(get_db)):
    """Devuelve el texto original y la versión simplificada con métricas de complejidad."""
    text = db.query(Text).filter(Text.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Texto no encontrado")

    original = text.content
    simplified = simplify_text(original, target_level="En Inicio")

    original_metrics = calculate_readability(original)
    simplified_metrics = calculate_readability(simplified)

    return {
        "id": text.id,
        "title": text.title,
        "level": text.level,
        "original": {
            "content": original,
            "metrics": original_metrics
        },
        "simplified": {
            "content": simplified,
            "metrics": simplified_metrics
        }
    }


@router.get("/", response_model=list[TextResponse])
def list_texts(db: Session = Depends(get_db)):
    texts = db.query(Text).all()
    return [
        TextResponse(id=t.id, title=t.title, content=t.content, level=t.level)
        for t in texts
    ]