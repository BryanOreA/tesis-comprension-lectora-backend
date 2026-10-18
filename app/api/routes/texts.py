import random
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.text import Text
from app.models.quiz import Quiz
from app.schemas.text import TextResponse, QuizItem
from app.services.nlp_service import simplify_text, calculate_readability

router = APIRouter(prefix="/texts", tags=["Textos"])


@router.get("/level/{level}", response_model=TextResponse)
def get_text_by_level(level: str, exclude_id: Optional[int] = None, db: Session = Depends(get_db)):
    # 1. Obtener textos del nivel
    texts = db.query(Text).filter(Text.level == level).all()
    
    if not texts:
        raise HTTPException(status_code=404, detail=f"No hay textos para el nivel '{level}'")

    # 2. Excluir el texto anterior si es que hay más de uno disponible
    if exclude_id and len(texts) > 1:
        filtered_texts = [t for t in texts if t.id != exclude_id]
        if filtered_texts:
            texts = filtered_texts

    # 3. Elegir al azar
    text = random.choice(texts)

    questions_db = db.query(Quiz).filter(Quiz.text_id == text.id).all()
    questions = []
    
    for q in questions_db:
        # Mezclar opciones
        options = [q.option_a, q.option_b, q.option_c, q.option_d]
        correct_idx = q.correct_answer
        
        combined = [(opt, i == correct_idx) for i, opt in enumerate(options)]
        random.shuffle(combined)
        
        new_options = [c[0] for c in combined]
        new_correct_answer = next(i for i, c in enumerate(combined) if c[1])

        questions.append(
            QuizItem(
                id=q.id,
                question=q.question,
                options=new_options,
                correctAnswer=new_correct_answer
            )
        )

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
        "original": {"content": original, "metrics": original_metrics},
        "simplified": {"content": simplified, "metrics": simplified_metrics}
    }


@router.get("/", response_model=list[TextResponse])
def list_texts(db: Session = Depends(get_db)):
    texts = db.query(Text).all()
    return [
        TextResponse(id=t.id, title=t.title, content=t.content, level=t.level)
        for t in texts
    ]