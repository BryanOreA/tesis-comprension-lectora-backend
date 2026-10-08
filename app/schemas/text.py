from pydantic import BaseModel
from typing import List

class QuizItem(BaseModel):
    id: int
    question: str
    options: List[str]
    correctAnswer: int

    class Config:
        from_attributes = True

class TextResponse(BaseModel):
    id: int
    title: str
    content: str
    level: str
    questions: List[QuizItem] = []