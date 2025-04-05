# We Hire Backend API

A FastAPI backend for the "We Hire" application that supports authentication, job management, and interview curriculum data.

## Features

- User authentication (signup and login) with JWT tokens
- Job management (CRUD operations)
- Interview curriculum data (categories and questions)
- Hiring manager information

## Tech Stack

- FastAPI: Modern, fast web framework for building APIs
- PostgreSQL: Relational database for data storage
- SQLAlchemy: ORM for database interactions
- Pydantic: Data validation and settings management
- JWT: Token-based authentication
- Uvicorn: ASGI server for running the application

## Project Structure

```
we_hire_backend/
├─ app/
│  ├─ main.py                  # FastAPI application entry point
│  ├─ models.py                # SQLAlchemy models
│  ├─ schemas.py               # Pydantic schemas
│  ├─ database.py              # Database connection setup
│  ├─ crud.py                  # CRUD functions
│  ├─ auth.py                  # Authentication functions
│  ├─ seed.py                  # Database seeding
│  ├─ config.py                # Configuration settings
│  ├─ routes/
│  │  ├─ auth_routes.py        # Auth endpoints
│  │  ├─ job_routes.py         # Job endpoints
│  │  ├─ interview_routes.py   # Interview endpoints
│  │  └─ hiring_routes.py      # Hiring manager endpoints
├─ requirements.txt            # Dependencies
├─ .env                        # Environment variables
└─ README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd we_hire_backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env` file:
```
DATABASE_URL=postgresql://username:password@localhost/we_hire_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Create the PostgreSQL database:
```sql
CREATE DATABASE we_hire_db;
```

### Running the Application

```bash
cd we_hire_backend
python -m uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

Interactive API documentation will be available at http://localhost:8000/docs

## API Endpoints

### Authentication

- `POST /api/auth/signup`: Register a new user
- `POST /api/auth/login`: Login and get access token

### Jobs

- `GET /api/jobs`: Get all jobs
- `GET /api/jobs/{job_id}`: Get a specific job
- `POST /api/jobs`: Create a new job
- `PUT /api/jobs/{job_id}`: Update a job
- `DELETE /api/jobs/{job_id}`: Delete a job

### Interview Curriculum

- `GET /api/interview/categories`: Get all interview categories
- `GET /api/interview/categories/{category_id}`: Get a specific category
- `POST /api/interview/categories`: Create a new category
- `POST /api/interview/questions`: Add a question to a category

### Hiring Managers

- `GET /api/hiring-managers`: Get all hiring managers

## Seed Data

The application includes seed data for testing:

- Users with different roles (HR, Hiring Manager, Employee)
- Sample job postings
- Interview categories and questions

## License

This project is licensed under the MIT License. # weHireBackend
