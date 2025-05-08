from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ResumeBase(BaseModel):
    filename: Optional[str] = None

class ResumeCreate(ResumeBase):
    content: str

class Resume(ResumeBase):
    id: int
    user_id: int
    content: str
    created_at: datetime
    
    class Config:
        orm_mode = True