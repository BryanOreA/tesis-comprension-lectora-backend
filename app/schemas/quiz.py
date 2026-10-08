from pydantic import BaseModel
from typing import List

class AnswerItem(BaseModel):
    questionId: int
    answer: int
    timeSpent: float = 0.0

class QuizSubmission(BaseModel):
    answers: List[AnswerItem]

class QuizResult(BaseModel):
    score: int
    total: int
    points: int
    newLevel: str