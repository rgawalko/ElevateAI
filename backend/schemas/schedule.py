from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict
from uuid import UUID

class ScheduleCreate(BaseModel):
    user_id: UUID
    date: datetime
    tasks: List[Dict]
    generated_by_ai: bool = False

class ScheduleOut(BaseModel):
    id: UUID
    user_id: UUID
    date: datetime
    tasks: List[Dict]
    generated_by_ai: bool
    created_at: datetime

    class Config:
        from_attributes = True
