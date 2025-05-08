from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import PyPDF2
import io
from datetime import timedelta
from typing import List, Optional

# Update these imports to the new app directory structure
from backend.app.database import get_db, engine
from backend.app.models import Base, User, Resume, Job, Match
from backend.app.schemas.user import UserCreate, User as UserSchema, Token
from backend.app.schemas.resume import ResumeCreate, Resume as ResumeSchema
from backend.app.schemas.job import JobCreate, Job as JobSchema
from backend.app.schemas.match import MatchCreate, Match as MatchSchema, JobMatch, ResumeMatches
from backend.app.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.app.llm import batch_compute_job_matches, extract_resume_info
# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Resume Matcher API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User endpoints
@app.post("/users/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Resume endpoints
@app.post("/resumes/", response_model=ResumeSchema)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Read and extract text from the uploaded file
    content = ""
    filename = file.filename
    
    # Handle PDF files
    if filename.lower().endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
        for page_num in range(len(pdf_reader.pages)):
            content += pdf_reader.pages[page_num].extract_text()
    # Handle text files
    elif filename.lower().endswith(('.txt', '.doc', '.docx')):
        content = (await file.read()).decode()
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    # Create and save resume
    resume = Resume(
        user_id=current_user.id,
        filename=filename,
        content=content
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return resume

@app.get("/resumes/", response_model=List[ResumeSchema])
def get_user_resumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes

@app.get("/resumes/{resume_id}", response_model=ResumeSchema)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

# Job endpoints
@app.post("/jobs/", response_model=JobSchema)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db)
):
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/jobs/", response_model=List[JobSchema])
def get_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs

@app.get("/jobs/{job_id}", response_model=JobSchema)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# Match endpoints
@app.post("/match/", response_model=ResumeMatches)
def match_resume_to_jobs(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get the resume
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Check if we have any jobs, if not create some sample jobs
    if db.query(Job).count() == 0:
        sample_jobs = [
            {
                "title": "Software Engineer",
                "description": "Looking for a software engineer with experience in Python, FastAPI, and PostgreSQL. Must have strong problem-solving skills and experience with RESTful APIs.",
                "company": "Tech Corp"
            },
            {
                "title": "Data Scientist",
                "description": "Seeking a data scientist with experience in machine learning, Python, and data analysis. Must have experience with pandas, numpy, and scikit-learn.",
                "company": "Data Insights"
            },
            {
                "title": "DevOps Engineer",
                "description": "Looking for a DevOps engineer with experience in Docker, Kubernetes, and CI/CD pipelines. Must have experience with cloud platforms like AWS or GCP.",
                "company": "Cloud Solutions"
            }
        ]
        for job_data in sample_jobs:
            job = Job(**job_data)
            db.add(job)
        db.commit()
    
    # Get all jobs
    jobs = db.query(Job).all()
    job_data = [{"id": job.id, "description": job.description} for job in jobs]
    
    # Compute matches using LLM
    matches = batch_compute_job_matches(resume.content, job_data)
    
    # Store matches in database
    for match in matches:
        # Check if match already exists
        existing_match = db.query(Match).filter(
            Match.resume_id == resume_id, 
            Match.job_id == match["job_id"]
        ).first()
        
        if existing_match:
            # Update existing match
            existing_match.score = match["score"]
        else:
            # Create new match
            db_match = Match(
                resume_id=resume_id,
                job_id=match["job_id"],
                score=match["score"]
            )
            db.add(db_match)
    
    db.commit()
    
    # Get top 5 matching jobs
    top_matches = []
    for match in matches[:5]:  # Limit to top 5
        job = db.query(Job).filter(Job.id == match["job_id"]).first()
        if job:
            # Convert ORM model to dictionary to fix the validation error
            job_dict = {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "location": "Remote",
                # Add any other fields required by your Job schema
                "created_at": job.created_at if hasattr(job, 'created_at') else None
            }
            
            top_matches.append(JobMatch(
                job=job_dict,  # Pass the dictionary instead of the ORM model
                score=match["score"]
            ))
    
    # Convert resume ORM model to dictionary for Pydantic validation
    resume_dict = {
        "id": resume.id,
        "user_id": resume.user_id,
        "filename": resume.filename,
        "content": resume.content,
        "created_at": resume.created_at if hasattr(resume, 'created_at') else None
    }
    
    return ResumeMatches(
        resume=resume_dict,  # Pass the dictionary instead of the ORM model
        matches=top_matches
    )
    
@app.get("/matches/{resume_id}", response_model=List[JobMatch])
def get_resume_matches(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify resume belongs to user
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get matches
    matches = db.query(Match).filter(Match.resume_id == resume_id).order_by(Match.score.desc()).all()
    
    # Build response
    result = []
    for match in matches:
        job = db.query(Job).filter(Job.id == match.job_id).first()
        if job:
            # Convert ORM model to dictionary
            job_dict = {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "location": "Remote",
                # Add any other fields required by your Job schema
                "created_at": job.created_at if hasattr(job, 'created_at') else None
            }
            result.append(JobMatch(job=job_dict, score=match.score))
    
    return result