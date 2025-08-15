from pydantic import BaseModel
from datetime import datetime
from typing import List
from uuid import UUID

class AIInsightCreate(BaseModel):
    user_id: UUID
    insight_type: str
    summary: str
    suggestions: List[str]

class AIInsightOut(BaseModel):
    id: UUID
    user_id: UUID
    insight_type: str
    summary: str
    suggestions: List[str]
    generated_at: datetime

    class Config:
        from_attributes = True
