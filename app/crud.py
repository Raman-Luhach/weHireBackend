from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas, auth

# User CRUD operations
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_hiring_managers(db: Session):
    return db.query(models.User).filter(models.User.role == "Hiring Manager").all()

# Job CRUD operations
def create_job(db: Session, job: schemas.JobCreate):
    db_job = models.Job(
        title=job.title,
        description=job.description,
        requirements=job.requirements,
        end_date=job.end_date,
        assigned_to=job.assigned_to,
        status=job.status,
        location=job.location,
        salary=job.salary,
        department=job.department,
        date_created=datetime.now().date()
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def get_jobs(db: Session, skip: int = 0, limit: int = 100, status: str = None, title: str = None):
    query = db.query(models.Job)
    
    if status:
        query = query.filter(models.Job.status == status)
    
    if title:
        query = query.filter(models.Job.title.ilike(f"%{title}%"))
    
    return query.offset(skip).limit(limit).all()

def get_jobs_by_manager(db: Session, manager_id: int, skip: int = 0, limit: int = 100):
    """Get jobs assigned to a specific manager."""
    return db.query(models.Job).filter(models.Job.assigned_to == manager_id).offset(skip).limit(limit).all()

def update_job(db: Session, job_id: int, job_update: schemas.JobUpdate):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if db_job:
        update_data = job_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_job, key, value)
        db.commit()
        db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: int):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if db_job:
        db.delete(db_job)
        db.commit()
    return db_job

# Interview Category CRUD operations
def create_interview_category(db: Session, category: schemas.InterviewCategoryCreate):
    db_category = models.InterviewCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_interview_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.InterviewCategory).offset(skip).limit(limit).all()

def get_interview_category(db: Session, category_id: int):
    return db.query(models.InterviewCategory).filter(models.InterviewCategory.id == category_id).first()

# Interview Question CRUD operations
def create_interview_question(db: Session, question: schemas.InterviewQuestionCreate):
    db_question = models.InterviewQuestion(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question 