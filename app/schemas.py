from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional, Union
from datetime import date, datetime
from enum import Enum

class UserRole(str, Enum):
    HR = "HR"
    HIRING_MANAGER = "Hiring Manager"
    EMPLOYEE = "Employee"
    OTHER = "Other"

class JobStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    DRAFT = "draft"
    IN_REVIEW = "in_review"

# User schemas
class UserBase(BaseModel):
    username: str
    role: UserRole = UserRole.OTHER

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None

# Job schemas
class JobBase(BaseModel):
    title: str
    description: str
    requirements: str
    end_date: Optional[date] = None
    status: JobStatus = JobStatus.DRAFT
    location: str
    salary: Optional[float] = None
    department: str

class JobCreate(JobBase):
    assigned_to: Optional[int] = None

class JobUpdate(JobBase):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    assigned_to: Optional[int] = None
    status: Optional[JobStatus] = None
    location: Optional[str] = None
    department: Optional[str] = None

class Job(JobBase):
    id: int
    date_created: Union[date, str]
    assigned_to: Optional[int] = None
    
    @validator('date_created', pre=True)
    def parse_date_created(cls, value):
        if value is None:
            return datetime.now().date()
        if isinstance(value, (date, str)):
            return value
        raise ValueError(f"Invalid date format: {value}")

    class Config:
        from_attributes = True

class JobDetail(Job):
    assigned_manager: Optional[User] = None

    class Config:
        from_attributes = True

# Interview Question schemas
class InterviewQuestionBase(BaseModel):
    text: str
    status: str = "active"
    must_ask: bool = False

class InterviewQuestionCreate(InterviewQuestionBase):
    category_id: int
    job_id: int

class InterviewQuestionUpdate(BaseModel):
    text: Optional[str] = None
    status: Optional[str] = None
    must_ask: Optional[bool] = None
    category_id: Optional[int] = None

class InterviewQuestion(InterviewQuestionBase):
    id: int
    category_id: int
    job_id: Optional[int] = None
    
    @validator('job_id', pre=True)
    def validate_job_id(cls, value):
        return value if value is not None else 0

    class Config:
        from_attributes = True

# Interview Category schemas
class InterviewCategoryBase(BaseModel):
    name: str
    description: str
    default_time: int

class InterviewCategoryCreate(InterviewCategoryBase):
    job_id: int

class InterviewCategory(InterviewCategoryBase):
    id: int
    job_id: Optional[int] = None
    questions: List[InterviewQuestion] = []
    
    @validator('job_id', pre=True)
    def validate_job_id(cls, value):
        return value if value is not None else 0

    class Config:
        from_attributes = True

# Default Interview Structure
class DefaultInterviewCategory(BaseModel):
    name: str
    description: str
    default_time: int
    questions: List[str]

# Candidate schemas
class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    education: str
    experience: str
    status: int = 0  # 0: Screening, 1: Interview, 2: Hired, 3: Rejected
    resume_url: Optional[str] = None
    cover_letter: bool = False
    skills: List[str]  # Will be converted to/from comma-separated string in CRUD operations
    rating: float = 0.0
    avatar_url: Optional[str] = None
    interview_scheduled: bool = False
    interview_date: Optional[datetime] = None
    notes: Optional[str] = None

class CandidateCreate(CandidateBase):
    job_id: int

class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    status: Optional[int] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[bool] = None
    skills: Optional[List[str]] = None
    rating: Optional[float] = None
    avatar_url: Optional[str] = None
    interview_scheduled: Optional[bool] = None
    interview_date: Optional[datetime] = None
    notes: Optional[str] = None

class Candidate(CandidateBase):
    id: int
    job_id: int
    applied_date: date

    @validator('skills', pre=True)
    def split_skills(cls, v):
        if isinstance(v, str):
            return [skill.strip() for skill in v.split(',') if skill.strip()]
        return v

    class Config:
        from_attributes = True 