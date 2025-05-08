# AI Resume Matcher

An intelligent application that uses AI to match resumes with job descriptions, helping job seekers optimize their applications and assisting recruiters in finding the best candidates.

## Overview

AI Resume Matcher analyzes resumes and job descriptions using natural language processing and machine learning to:
- Score resume-job compatibility
- Highlight matching skills and qualifications
- Suggest improvements to increase match scores
- Provide insights for both job seekers and recruiters

**Note:** The current version works with test job descriptions only and does not search the internet for real job listings. This functionality may be added in future updates.

## Features

- **Resume Analysis**: Upload and analyze resumes in various formats
- **Job Description Parsing**: Extract key requirements and qualifications from job postings
- **AI-Powered Matching**: Advanced algorithms to determine compatibility scores
- **Improvement Suggestions**: Get actionable feedback to optimize your resume
- **User Authentication**: Secure login and profile management
- **Dashboard**: Visualize match scores and track progress

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: Python-based web interface
- **Database**: SQL database (via SQLAlchemy)
- **AI/ML**: Natural Language Processing models
- **Containerization**: Docker for easy deployment

## Project Structure

```
ai-resume-matcher/
├── backend/               # FastAPI backend
│   ├── app/               # Application code
│   │   ├── routers/       # API endpoints
│   │   ├── schemas/       # Pydantic models
│   │   ├── auth.py        # Authentication logic
│   │   ├── database.py    # Database connection
│   │   ├── llm.py         # Language model integration
│   │   └── models.py      # Database models
│   ├── Dockerfile         # Backend container configuration
│   ├── main.py            # Application entry point
│   ├── requirements.txt   # Python dependencies
│   └── seed_data.py       # Initial data for development
├── frontend/              # Web interface
│   ├── components/        # UI components
│   ├── utils/             # Utility functions
│   ├── app.py             # Frontend application
│   ├── Dockerfile         # Frontend container configuration
│   └── requirements.txt   # Frontend dependencies
├── docker-compose.yml     # Multi-container configuration
├── .env                   # Environment variables (not tracked in Git)
├── poetry.lock            # Dependency lock file
├── pyproject.toml         # Project configuration
└── setup.sh               # Setup script
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AdamDamreh/AI-Resume-Matcher-Test.git
   cd AI-Resume-Matcher-Test
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. Start the application:
   ```bash
   docker-compose up -d
   ```

5. Access the application:
   - Frontend: http://localhost:8501
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Usage

### For Job Seekers

1. Create an account and log in
2. Upload your resume
3. Search for job descriptions or paste them directly
4. Get match scores and suggestions for improvement
5. Update your resume based on feedback
6. Track your progress over time

### For Recruiters

1. Create an account and log in
2. Upload job descriptions
3. Review matched candidates
4. Filter and sort by match scores
5. Export reports and analytics

## Development

### Running Locally Without Docker

1. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Run the backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

4. Run the frontend (in a separate terminal):
   ```bash
   cd frontend
   streamlit run app.py
   ```

### Running Tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Future Enhancements

- Integration with job boards to fetch real job listings
- Enhanced matching algorithms with more advanced AI models
- Mobile application for on-the-go resume optimization
- Employer portal with advanced analytics

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the open-source AI and NLP communities
