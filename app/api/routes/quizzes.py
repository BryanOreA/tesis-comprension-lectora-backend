from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.quiz import Quiz
from app.models.progress import Progress
from app.schemas.quiz import QuizSubmission, QuizResult
from app.services.ml_service import classify_level

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.post("/{text_id}/submit", response_model=QuizResult)
def submit_quiz(text_id: int, submission: QuizSubmission, student_id: int = 1, db: Session = Depends(get_db)):
    questions = db.query(Quiz).filter(Quiz.text_id == text_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="Quiz no encontrado")

    correct_count = 0
    total_time = 0.0
    for answer in submission.answers:
        q = next((q for q in questions if q.id == answer.questionId), None)
        if q and q.correct_answer == answer.answer:
            correct_count += 1
        total_time += answer.timeSpent

    total = len(questions)
    percentage = (correct_count / total) * 100 if total else 0
    avg_time = total_time / max(len(submission.answers), 1)

    new_level = classify_level(
        percentage=percentage,
        avg_time=avg_time,
        attempts=len(submission.answers),
        help_used=0
    )

    progress = Progress(
        student_id=student_id,
        text_id=text_id,
        score=correct_count,
        total_questions=total,
        time_spent=total_time,
        level=new_level,
        points_earned=correct_count * 10
    )
    db.add(progress)
    db.commit()

    return QuizResult(
        score=correct_count,
        total=total,
        points=correct_count * 10,
        newLevel=new_level
    )