from pydantic import BaseModel
from typing import List, Dict

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    text: str

class CompleteRequest(BaseModel):
    answers: Dict[str, str]
    transcript: List[ChatMessage]

class AnswerRequest(BaseModel):
    message: str

