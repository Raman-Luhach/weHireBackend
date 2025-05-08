from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas, auth
from typing import Optional

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
        department=job.department
        # date_created is handled by the server_default
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Create default interview categories and questions for this job
    create_default_interview_structure(db, db_job.id)
    
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

def get_interview_categories_by_job(db: Session, job_id: int):
    """Get all interview categories for a specific job."""
    return db.query(models.InterviewCategory).filter(models.InterviewCategory.job_id == job_id).all()

def get_interview_category(db: Session, category_id: int):
    return db.query(models.InterviewCategory).filter(models.InterviewCategory.id == category_id).first()

def delete_interview_category(db: Session, category_id: int):
    """Delete an interview category and all its related questions."""
    db_category = db.query(models.InterviewCategory).filter(models.InterviewCategory.id == category_id).first()
    if db_category:
        db.delete(db_category)  # Will cascade delete related questions
        db.commit()
        return True
    return False

# Interview Question CRUD operations
def create_interview_question(db: Session, question: schemas.InterviewQuestionCreate):
    db_question = models.InterviewQuestion(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_interview_questions_by_job(db: Session, job_id: int):
    """Get all interview questions for a specific job."""
    return db.query(models.InterviewQuestion).filter(models.InterviewQuestion.job_id == job_id).all()

def get_interview_questions_by_category(db: Session, category_id: int, job_id: Optional[int] = None):
    """Get all interview questions for a specific category and optionally for a specific job."""
    query = db.query(models.InterviewQuestion).filter(models.InterviewQuestion.category_id == category_id)
    
    if job_id is not None:
        query = query.filter(models.InterviewQuestion.job_id == job_id)
    
    return query.all()

def get_interview_question(db: Session, question_id: int):
    """Get an interview question by its ID."""
    return db.query(models.InterviewQuestion).filter(models.InterviewQuestion.id == question_id).first()

def update_interview_question(db: Session, question_id: int, question_update: schemas.InterviewQuestionUpdate):
    """Update an interview question."""
    db_question = get_interview_question(db, question_id)
    if db_question:
        update_data = question_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
    return db_question

def delete_interview_question(db: Session, question_id: int):
    """Delete an interview question."""
    db_question = get_interview_question(db, question_id)
    if db_question:
        db.delete(db_question)
        db.commit()
    return db_question

# Default interview structure creation
def create_default_interview_structure(db: Session, job_id: int):
    """
    Create default interview categories and questions for a new job.
    This is called automatically when a new job is created.
    """
    default_categories = [
        {
            "name": "Technical Skills",
            "description": "Questions about technical knowledge and skills",
            "default_time": 45,
            "questions": [
                {"text": "Explain the difference between a list and a dictionary in Python.", "must_ask": True},
                {"text": "What is dependency injection and why is it useful?", "must_ask": False},
                {"text": "Explain the concept of state management in frontend frameworks.", "must_ask": True}
            ]
        },
        {
            "name": "Problem Solving",
            "description": "Questions to assess problem-solving abilities",
            "default_time": 60,
            "questions": [
                {"text": "How would you design a URL shortening service?", "must_ask": True},
                {"text": "Describe a challenging problem you faced and how you solved it.", "must_ask": False},
                {"text": "How would you optimize a slow API endpoint?", "must_ask": True}
            ]
        },
        {
            "name": "Behavioral",
            "description": "Questions about work style and behavior",
            "default_time": 30,
            "questions": [
                {"text": "Tell me about a time when you had to work under a tight deadline.", "must_ask": True},
                {"text": "How do you handle conflicts in a team?", "must_ask": True},
                {"text": "Describe a situation where you had to learn a new technology quickly.", "must_ask": False}
            ]
        }
    ]
    
    for category_data in default_categories:
        questions = category_data.pop("questions")
        
        db_category = models.InterviewCategory(
            name=category_data["name"],
            description=category_data["description"],
            default_time=category_data["default_time"],
            job_id=job_id
        )
        db.add(db_category)
        db.flush()  # To get the category ID
        
        for question in questions:
            db_question = models.InterviewQuestion(
                text=question["text"],
                status="active",
                must_ask=question["must_ask"],
                category_id=db_category.id,
                job_id=job_id
            )
            db.add(db_question)
    
    db.commit()

def clone_interview_structure(db: Session, source_job_id: int, target_job_id: int, clone_questions: bool = False):
    """
    Clone interview categories from one job to another.
    Optionally clone the questions as well.
    
    Args:
        db: Database session
        source_job_id: ID of the job to clone from
        target_job_id: ID of the job to clone to
        clone_questions: Whether to also clone the questions
        
    Returns:
        List of created interview categories
    """
    # Check if source and target jobs exist
    source_job = get_job(db, job_id=source_job_id)
    target_job = get_job(db, job_id=target_job_id)
    
    if not source_job or not target_job:
        return None
    
    # Get all categories from source job
    source_categories = get_interview_categories_by_job(db, job_id=source_job_id)
    created_categories = []
    
    for source_category in source_categories:
        # Create a new category for the target job
        new_category = models.InterviewCategory(
            name=source_category.name,
            description=source_category.description,
            default_time=source_category.default_time,
            job_id=target_job_id
        )
        db.add(new_category)
        db.flush()  # To get the new category ID
        
        # If clone_questions is True, clone the questions as well
        if clone_questions:
            # Get all questions for this category in the source job
            source_questions = get_interview_questions_by_category(
                db, 
                category_id=source_category.id, 
                job_id=source_job_id
            )
            
            for source_question in source_questions:
                new_question = models.InterviewQuestion(
                    text=source_question.text,
                    status=source_question.status,
                    must_ask=source_question.must_ask,
                    category_id=new_category.id,
                    job_id=target_job_id
                )
                db.add(new_question)
        
        created_categories.append(new_category)
    
    db.commit()
    return created_categories

# Candidate CRUD operations
def create_candidate(db: Session, candidate: schemas.CandidateCreate):
    """Create a new candidate."""
    # Convert skills list to comma-separated string
    candidate_data = candidate.dict()
    candidate_data['skills'] = ','.join(candidate_data['skills'])
    
    db_candidate = models.Candidate(**candidate_data)
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

def get_candidate(db: Session, candidate_id: int):
    """Get a candidate by ID."""
    return db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()

def get_candidates_by_job(db: Session, job_id: int, skip: int = 0, limit: int = 100):
    """Get all candidates for a specific job."""
    return db.query(models.Candidate).filter(
        models.Candidate.job_id == job_id
    ).offset(skip).limit(limit).all()

def update_candidate(db: Session, candidate_id: int, candidate_update: schemas.CandidateUpdate):
    """Update a candidate's information."""
    db_candidate = get_candidate(db, candidate_id=candidate_id)
    if db_candidate:
        update_data = candidate_update.dict(exclude_unset=True)
        
        # Convert skills list to comma-separated string if skills are being updated
        if 'skills' in update_data and update_data['skills'] is not None:
            update_data['skills'] = ','.join(update_data['skills'])
        
        for key, value in update_data.items():
            setattr(db_candidate, key, value)
        
        db.commit()
        db.refresh(db_candidate)
    return db_candidate

def delete_candidate(db: Session, candidate_id: int):
    """Delete a candidate."""
    db_candidate = get_candidate(db, candidate_id=candidate_id)
    if db_candidate:
        db.delete(db_candidate)
        db.commit()
    return db_candidate

def search_candidates(
    db: Session,
    job_id: int,
    search_term: Optional[str] = None,
    status: Optional[int] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Search candidates with filters.
    status: Integer (0: Screening, 1: Interview, 2: Hired, 3: Rejected)
    """
    query = db.query(models.Candidate).filter(models.Candidate.job_id == job_id)
    
    if search_term:
        search_term = f"%{search_term}%"
        query = query.filter(
            (models.Candidate.name.ilike(search_term)) |
            (models.Candidate.email.ilike(search_term)) |
            (models.Candidate.education.ilike(search_term)) |
            (models.Candidate.experience.ilike(search_term)) |
            (models.Candidate.skills.ilike(search_term))
        )
    
    if status is not None:
        query = query.filter(models.Candidate.status == status)
    
    if min_rating is not None:
        query = query.filter(models.Candidate.rating >= min_rating)
    
    if max_rating is not None:
        query = query.filter(models.Candidate.rating <= max_rating)
    
    return query.offset(skip).limit(limit).all()

def get_candidate_status_counts(db: Session, job_id: int):
    """
    Get the count of candidates for each status for a specific job.
    Returns a dictionary with status counts:
    {
        "0": 5,  # 5 candidates in Screening
        "1": 3,  # 3 candidates in Interview
        "2": 1,  # 1 candidate Hired
        "3": 2   # 2 candidates Rejected
    }
    """
    result = {}
    
    # Query the database for counts of each status
    for status_value in [0, 1, 2, 3]:
        count = db.query(models.Candidate).filter(
            models.Candidate.job_id == job_id,
            models.Candidate.status == status_value
        ).count()
        result[str(status_value)] = count
    
    # Also get total count
    total = db.query(models.Candidate).filter(
        models.Candidate.job_id == job_id
    ).count()
    result["total"] = total
    
    return result 