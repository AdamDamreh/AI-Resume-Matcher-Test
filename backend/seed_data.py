import requests
import time
import os

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Sample job data
sample_jobs = [
    {
        "title": "Software Engineer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "description": """
        We are looking for a skilled Software Engineer to join our team!
        
        Requirements:
        - Bachelor's degree in Computer Science or related field
        - 3+ years of experience in software development
        - Proficient in Python, JavaScript, and SQL
        - Experience with web frameworks like Django or Flask
        - Knowledge of cloud services (AWS, Azure, or GCP)
        - Strong problem-solving skills
        
        Responsibilities:
        - Develop and maintain high-quality software
        - Collaborate with cross-functional teams
        - Write clean, efficient, and maintainable code
        - Participate in code reviews and documentation
        - Stay up-to-date with emerging trends in technology
        """
    },
    {
        "title": "Data Scientist",
        "company": "DataGenius",
        "location": "New York, NY",
        "description": """
        Join our data science team to solve complex problems with data!
        
        Requirements:
        - MS or PhD in Statistics, Mathematics, Computer Science, or related field
        - Strong programming skills in Python and R
        - Experience with data manipulation libraries (Pandas, NumPy)
        - Knowledge of machine learning frameworks (scikit-learn, TensorFlow, PyTorch)
        - Experience with big data technologies (Spark, Hadoop)
        - Excellent communication skills
        
        Responsibilities:
        - Develop machine learning models and algorithms
        - Analyze large datasets to discover patterns and insights
        - Create data visualizations and reports
        - Collaborate with product and engineering teams
        - Stay current with state-of-the-art methods and technologies
        """
    },
    {
        "title": "Frontend Developer",
        "company": "WebWizards",
        "location": "Seattle, WA",
        "description": """
        Looking for a creative Frontend Developer to build amazing user experiences!
        
        Requirements:
        - 2+ years of experience in frontend development
        - Strong knowledge of HTML, CSS, and JavaScript
        - Experience with frontend frameworks (React, Angular, or Vue)
        - Understanding of responsive design and cross-browser compatibility
        - Knowledge of state management (Redux, MobX, or similar)
        - Eye for design and user experience
        
        Responsibilities:
        - Implement user interfaces based on designs
        - Ensure the technical feasibility of UI/UX designs
        - Optimize applications for maximum speed and scalability
        - Collaborate with the backend team to integrate frontend and backend
        - Stay up-to-date with emerging frontend technologies
        """
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudMasters",
        "location": "Austin, TX",
        "description": """
        Join our DevOps team to build and maintain our cloud infrastructure!
        
        Requirements:
        - 4+ years of experience in a DevOps or SRE role
        - Strong knowledge of Linux/Unix systems
        - Experience with cloud platforms (AWS, GCP, or Azure)
        - Proficiency with infrastructure as code (Terraform, CloudFormation)
        - Experience with containerization (Docker, Kubernetes)
        - Knowledge of CI/CD pipelines (Jenkins, GitLab CI, or GitHub Actions)
        
        Responsibilities:
        - Design, implement, and maintain CI/CD pipelines
        - Manage cloud infrastructure and automate deployments
        - Monitor systems and applications for performance and reliability
        - Troubleshoot and resolve issues in development, testing, and production
        - Work closely with development teams to improve delivery processes
        """
    },
    {
        "title": "Product Manager",
        "company": "ProductPros",
        "location": "Chicago, IL",
        "description": """
        We're looking for a Product Manager to lead our product development!
        
        Requirements:
        - 3+ years of experience in product management
        - Strong understanding of software development lifecycle
        - Experience with agile methodologies
        - Excellent communication and leadership skills
        - Data-driven approach to decision making
        - Technical background preferred
        
        Responsibilities:
        - Define product vision, strategy, and roadmap
        - Gather and prioritize product requirements
        - Work with engineering, design, and marketing teams
        - Analyze market trends and competitive landscape
        - Define and track success metrics for products
        """
    }
]

# Sample user
sample_user = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password123"
}

def seed_data():
    """Seed the database with sample data"""
    print("Seeding database with sample data...")
    
    # Create user
    try:
        response = requests.post(f"{API_URL}/users/", json=sample_user)
        if response.status_code == 200:
            print(f"Created user: {sample_user['username']}")
        elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
            print(f"User {sample_user['username']} already exists")
        else:
            print(f"Failed to create user: {response.json()}")
            return
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return
    
    # Login to get token
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": sample_user["username"], "password": sample_user["password"]}
        )
        if response.status_code != 200:
            print(f"Failed to login: {response.json()}")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"Error logging in: {str(e)}")
        return
    
    # Add jobs
    for job in sample_jobs:
        try:
            response = requests.post(f"{API_URL}/jobs/", json=job)
            if response.status_code == 200:
                print(f"Created job: {job['title']}")
            else:
                print(f"Failed to create job: {response.json()}")
        except Exception as e:
            print(f"Error creating job: {str(e)}")
    
    print("Seeding completed!")

if __name__ == "__main__":
    # Wait for backend to be available
    max_retries = 30
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.get(f"{API_URL}/jobs/")
            if response.status_code == 200:
                print("Backend is available. Starting seeding...")
                break
        except:
            pass
        
        print("Waiting for backend to be available...")
        time.sleep(2)
        retry_count += 1
    
    if retry_count == max_retries:
        print("Backend not available after maximum retries. Exiting.")
        exit(1)
    
    seed_data()