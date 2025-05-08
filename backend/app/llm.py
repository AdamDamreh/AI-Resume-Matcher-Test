import os
import json
import google.generativeai as genai
from typing import List, Dict, Any
from fastapi import HTTPException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Gemini API with your API key (from environment variable)
API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key is available
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set this variable to use the Gemini API.")

# Configure the API
genai.configure(api_key=API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_resume_info(resume_text: str) -> Dict[str, Any]:
    """Extract structured information from resume text using Gemini"""
    try:
        prompt = f"""
        Extract key information from this resume in JSON format. Include:
        - skills (list of technical and soft skills)
        - experience (list of work experiences with company, title, duration)
        - education (list of degrees with institution, degree, field, year)

        Resume:
        {resume_text}

        Return ONLY valid JSON.
        """
        
        response = model.generate_content(prompt)
        try:
            # Extract the JSON part from the response
            return json.loads(response.text)
        except:
            # Fallback if JSON parsing fails
            return {
                "skills": [],
                "experience": [],
                "education": []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Gemini API: {str(e)}")

def compute_job_match(resume_text: str, job_description: str) -> float:
    """
    Use Gemini to compute match score between resume and job description
    Returns a score between 0 and 1
    """
    try:
        prompt = f"""
        Analyze the compatibility between the resume and job description below.
        Evaluate how well the candidate's skills, experience, and qualifications match the job requirements.
        
        Resume:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Return ONLY a score between 0 and 1 (where 1 is a perfect match), with no explanation.
        """
        
        response = model.generate_content(prompt)
        try:
            # Try to parse the score as a float
            score = float(response.text.strip())
            # Ensure the score is between 0 and 1
            return max(0, min(score, 1))
        except:
            # Fallback if parsing fails
            return 0.5
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Gemini API: {str(e)}")

def batch_compute_job_matches(resume_text: str, job_descriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compute match scores for multiple jobs at once
    Returns list of jobs with match scores
    """
    matches = []
    
    for job in job_descriptions:
        score = compute_job_match(resume_text, job["description"])
        matches.append({
            "job_id": job["id"],
            "score": score
        })
    
    # Sort by score in descending order
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches