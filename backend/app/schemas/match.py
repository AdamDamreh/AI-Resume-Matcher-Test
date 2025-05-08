from pydantic import BaseModel
from datetime import datetime
from typing import List
from .job import Job
from .resume import Resume

class MatchBase(BaseModel):
    resume_id: int
    job_id: int
    score: float

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class JobMatch(BaseModel):
    job: Job
    score: float

class ResumeMatches(BaseModel):
    resume: Resume
    matches: List[JobMatch]