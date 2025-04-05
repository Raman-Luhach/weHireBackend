from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Date, Float, Enum
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
    date_created = Column(Date, default=datetime.now().date)
    end_date = Column(Date)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default=JobStatus.DRAFT)
    location = Column(String)
    salary = Column(Float, nullable=True)
    department = Column(String)
    
    # Relationship with the assigned hiring manager
    assigned_manager = relationship("User", back_populates="assigned_jobs")

class InterviewCategory(Base):
    __tablename__ = "interview_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    default_time = Column(Integer)  # in minutes
    
    # Relationship with interview questions
    questions = relationship("InterviewQuestion", back_populates="category")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    status = Column(String, default="active")
    category_id = Column(Integer, ForeignKey("interview_categories.id"))
    
    # Relationship with category
    category = relationship("InterviewCategory", back_populates="questions") 