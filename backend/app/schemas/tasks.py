from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class TaskOut(BaseModel):
    id: str
    title: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    due_at: Optional[datetime]
    assignee_id: Optional[str]
    meta: Dict = {}