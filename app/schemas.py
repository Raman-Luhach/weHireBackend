from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
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
        orm_mode = True

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
    date_created: date
    assigned_to: Optional[int] = None

    class Config:
        orm_mode = True

class JobDetail(Job):
    assigned_manager: Optional[User] = None

    class Config:
        orm_mode = True

# Interview Question schemas
class InterviewQuestionBase(BaseModel):
    text: str
    status: str = "active"

class InterviewQuestionCreate(InterviewQuestionBase):
    category_id: int

class InterviewQuestion(InterviewQuestionBase):
    id: int
    category_id: int

    class Config:
        orm_mode = True

# Interview Category schemas
class InterviewCategoryBase(BaseModel):
    name: str
    description: str
    default_time: int

class InterviewCategoryCreate(InterviewCategoryBase):
    pass

class InterviewCategory(InterviewCategoryBase):
    id: int
    questions: List[InterviewQuestion] = []

    class Config:
        orm_mode = True 