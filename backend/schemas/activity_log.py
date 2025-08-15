from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID

class ActivityLogCreate(BaseModel):
    user_id: UUID
    date: datetime
    activities: List[Dict]
    notes: Optional[str] = None

class ActivityLogOut(BaseModel):
    id: UUID
    user_id: UUID
    date: datetime
    activities: List[Dict]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
