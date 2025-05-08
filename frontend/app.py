import streamlit as st
import requests
import json
import pandas as pd
from io import StringIO
import os
#include sql imports 

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="AI Resume Matcher",
    page_icon="📄",
    layout="wide"
)

# Session state initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "current_resume" not in st.session_state:
    st.session_state.current_resume = None
if "job_matches" not in st.session_state:
    st.session_state.job_matches = None

# Helper functions
def login(username, password):
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            
            # Get user info
            user_response = requests.get(
                f"{API_URL}/users/me/",
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )
            if user_response.status_code == 200:
                st.session_state.user = user_response.json()
                return True
        return False
    except Exception as e:
        st.error(f"Error during login: {str(e)}")
        return False

def register(username, email, password):
    try:
        response = requests.post(
            f"{API_URL}/users/",
            json={"username": username, "email": email, "password": password}
        )
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error during registration: {str(e)}")
        return False

def upload_resume(file):
    try:
        files = {"file": file}
        response = requests.post(
            f"{API_URL}/resumes/",
            files=files,
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            resume_data = response.json()
            st.session_state.current_resume = resume_data
            return True
        else:
            st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error during upload: {str(e)}")
        return False

def get_user_resumes():
    try:
        response = requests.get(
            f"{API_URL}/resumes/",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

def match_resume(resume_id):
    try:
        # First try to get matches from the GET endpoint instead
        post_response = requests.post(
            f"{API_URL}/match/?resume_id={resume_id}",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if post_response.status_code == 200:
            # After successful POST, get the matches using GET endpoint
            get_response = requests.get(
                f"{API_URL}/matches/{resume_id}",
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )
            
            if get_response.status_code == 200:
                try:
                    match_data = get_response.json()
                    # Debugging the actual response
                    st.write("DEBUG - API Response (GET matches):", match_data)
                    
                    # Store the matches directly
                    st.session_state.job_matches = match_data
                    st.success("Resume matched with jobs!")
                    return True
                except json.JSONDecodeError as e:
                    st.error(f"Invalid response format from server: {str(e)}")
                    st.error(f"Response content: {get_response.text}")
                    return False
            else:
                st.error(f"Failed to retrieve matches after successful matching: {get_response.text}")
                return False
        else:
            st.error(f"Matching failed with status code {post_response.status_code}: {post_response.text}")
            return False
                
    except Exception as e:
        st.error(f"Error during matching: {str(e)}")
        return False

def get_job_details(job_id):
    try:
        response = requests.get(
            f"{API_URL}/jobs/{job_id}",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def logout():
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.current_resume = None
    st.session_state.job_matches = None

# Main app
def main():
    st.title("AI Resume Matcher")
    
    # Authentication
    if not st.session_state.token:
        auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])
        
        with auth_tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Login")
                
                if submit_button:
                    if login(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Login failed. Please check your credentials.")
        
        with auth_tab2:
            with st.form("register_form"):
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                register_button = st.form_submit_button("Register")
                
                if register_button:
                    if new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif register(new_username, new_email, new_password):
                        st.success("Registration successful! Please login.")
                        st.rerun()
    
    else:
        # User is logged in
        st.sidebar.write(f"Logged in as: {st.session_state.user['username']}")
        if st.sidebar.button("Logout"):
            logout()
            st.rerun()
        
        # Main content
        tab1, tab2 = st.tabs(["Upload Resume", "View Matches"])
        
        with tab1:
            st.header("Upload Your Resume")
            
            # Resume upload
            uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "txt", "doc", "docx"])
            
            if uploaded_file is not None:
                if st.button("Upload and Analyze"):
                    with st.spinner("Uploading and analyzing resume..."):
                        if upload_resume(uploaded_file):
                            st.success(f"Resume '{uploaded_file.name}' uploaded successfully!")
                            
                            # Automatically match the resume with jobs
                            with st.spinner("Matching with jobs..."):
                                if match_resume(st.session_state.current_resume["id"]):
                                    st.success("Resume matched with jobs!")
                                    st.rerun()
            
            # Previous resumes
            st.subheader("Your Previous Resumes")
            resumes = get_user_resumes()
            
            if resumes:
                resume_names = [f"{r['filename']} (ID: {r['id']})" for r in resumes]
                selected_resume = st.selectbox("Select a resume", resume_names)
                
                if selected_resume:
                    resume_id = int(selected_resume.split("ID: ")[1].strip(")"))
                    if st.button("Match with Jobs"):
                        with st.spinner("Matching resume with jobs..."):
                            # Find the selected resume in the list
                            for resume in resumes:
                                if resume["id"] == resume_id:
                                    st.session_state.current_resume = resume
                                    break
                                    
                            if match_resume(resume_id):
                                st.success("Resume matched with jobs!")
                                st.rerun()
            else:
                st.info("You have no resumes uploaded yet.")
        
        with tab2:
            st.header("Job Matches")
            
            if st.session_state.job_matches:
                # Display job matches in a table
                match_data = []
                for match in st.session_state.job_matches:
                    job = match["job"]
                    match_data.append({
                        "Job ID": job["id"],
                        "Title": job["title"],
                        "Company": job["company"],
                        "Location": job["location"],
                        "Match Score": f"{match['score']:.2%}"
                    })
                
                df = pd.DataFrame(match_data)
                st.dataframe(df, use_container_width=True)
                
                # Job details
                st.subheader("Job Details")
                job_ids = [match["job"]["id"] for match in st.session_state.job_matches]
                selected_job_id = st.selectbox("Select a job to view details", job_ids)
                
                if selected_job_id:
                    # Find job in matches
                    selected_job = None
                    selected_score = 0
                    for match in st.session_state.job_matches:
                        if match["job"]["id"] == selected_job_id:
                            selected_job = match["job"]
                            selected_score = match["score"]
                            break
                    
                    if selected_job:
                        st.write(f"**Title:** {selected_job['title']}")
                        st.write(f"**Company:** {selected_job['company']}")
                        st.write(f"**Location:** {selected_job['location']}")
                        st.write(f"**Match Score:** {selected_score:.2%}")
                        
                        st.write("**Job Description:**")
                        st.write(selected_job['description'])
                        
                        # Resume comparison (optional)
                        if st.button("Show Resume Comparison"):
                            with st.spinner("Analyzing match..."):
                                st.subheader("Why You Match")
                                
                                # Call Gemini API to explain the match
                                try:
                                    # This would be a direct call to the LLM API
                                    # For now, we'll just display a placeholder
                                    st.info("This feature requires integration with the backend LLM service.")
                                except Exception as e:
                                    st.error(f"Error generating comparison: {str(e)}")
            else:
                if st.session_state.current_resume:
                    st.info("No job matches found. Please go to the 'Upload Resume' tab and click 'Match with Jobs'.")
                else:
                    st.info("Please upload a resume first to see job matches.")

if __name__ == "__main__":
    main()