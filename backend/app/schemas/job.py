from pydantic import BaseModel
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company: str
    location: str = None
    description: str

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True