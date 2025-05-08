from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Date, Float, DateTime, Enum, func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from .database import Base

class UserRole(str, enum.Enum):
    HR = "HR"
    HIRING_MANAGER = "Hiring Manager"
    EMPLOYEE = "Employee"
    OTHER = "Other"

class JobStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    DRAFT = "draft"
    IN_REVIEW = "in_review"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.OTHER)
    
    # Relationship with jobs (for hiring managers)
    assigned_jobs = relationship("Job", back_populates="assigned_manager")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    requirements = Column(Text)
    date_created = Column(Date, nullable=False, server_default=func.current_date())
    end_date = Column(Date)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default=JobStatus.DRAFT)
    location = Column(String)
    salary = Column(Float, nullable=True)
    department = Column(String)
    
    # Relationship with the assigned hiring manager
    assigned_manager = relationship("User", back_populates="assigned_jobs")
    
    # Relationship with interview categories
    interview_categories = relationship("InterviewCategory", back_populates="job")

    # Relationship with candidates
    candidates = relationship("Candidate", back_populates="job", cascade="all, delete-orphan")

class InterviewCategory(Base):
    __tablename__ = "interview_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    default_time = Column(Integer)  # in minutes
    job_id = Column(Integer, ForeignKey("jobs.id"))
    
    # Relationship with interview questions
    questions = relationship("InterviewQuestion", back_populates="category", cascade="all, delete-orphan")
    
    # Relationship with job
    job = relationship("Job", back_populates="interview_categories")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    status = Column(String, default="active")
    must_ask = Column(Boolean, default=False)  # Indicates if this is a must-ask question
    category_id = Column(Integer, ForeignKey("interview_categories.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    
    # Relationship with category
    category = relationship("InterviewCategory", back_populates="questions")
    
    # Relationship with job
    job = relationship("Job")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    education = Column(Text)
    experience = Column(Text)
    applied_date = Column(Date, server_default=func.current_date())
    status = Column(Integer, default=0)  # 0: Screening, 1: Interview, 2: Hired, 3: Rejected
    resume_url = Column(String, nullable=True)
    cover_letter = Column(Boolean, default=False)
    skills = Column(Text)  # Store as comma-separated values
    rating = Column(Float, default=0.0)
    avatar_url = Column(String, nullable=True)
    interview_scheduled = Column(Boolean, default=False)
    interview_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))

    # Relationship with job
    job = relationship("Job", back_populates="candidates") 