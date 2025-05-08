from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from .. import schemas, crud, models, auth
from ..database import get_db

router = APIRouter(prefix="/api/interview", tags=["Interview"])

@router.get("/categories", response_model=List[schemas.InterviewCategory])
async def read_interview_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    categories = crud.get_interview_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/job/{job_id}/categories", response_model=List[schemas.InterviewCategory])
async def read_interview_categories_by_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all interview categories for a specific job."""
    # Check if job exists
    job = crud.get_job(db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
        
    categories = crud.get_interview_categories_by_job(db, job_id=job_id)
    return categories

@router.get("/job/{job_id}/questions", response_model=List[schemas.InterviewQuestion])
async def read_interview_questions_by_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all interview questions for a specific job."""
    # Check if job exists
    job = crud.get_job(db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
        
    questions = crud.get_interview_questions_by_job(db, job_id=job_id)
    return questions

@router.get("/categories/{category_id}", response_model=schemas.InterviewCategory)
async def read_interview_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_category = crud.get_interview_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Interview category not found")
    return db_category

@router.get("/categories/{category_id}/questions", response_model=List[schemas.InterviewQuestion])
async def read_interview_questions_by_category(
    category_id: int,
    job_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all interview questions for a specific category.
    Optionally filter by job_id if provided.
    """
    # Check if category exists
    category = crud.get_interview_category(db, category_id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Interview category not found")
    
    # If job_id is provided, check if it exists
    if job_id is not None:
        job = crud.get_job(db, job_id=job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        
    # Get questions, filtered by job_id if provided
    questions = crud.get_interview_questions_by_category(db, category_id=category_id, job_id=job_id)
    return questions

@router.post("/categories", response_model=schemas.InterviewCategory)
async def create_interview_category(
    category: schemas.InterviewCategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Only HR or Hiring Manager can create categories
    if current_user.role not in ["HR", "Hiring Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if job exists
    job = crud.get_job(db, job_id=category.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return crud.create_interview_category(db=db, category=category)

@router.post("/questions", response_model=schemas.InterviewQuestion)
async def create_interview_question(
    question: schemas.InterviewQuestionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Only HR or Hiring Manager can create questions
    if current_user.role not in ["HR", "Hiring Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if category exists
    db_category = crud.get_interview_category(db, category_id=question.category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Interview category not found")
    
    # Check if job exists
    job = crud.get_job(db, job_id=question.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if category belongs to the same job
    if db_category.job_id != question.job_id:
        raise HTTPException(status_code=400, detail="Category does not belong to the specified job")
    
    return crud.create_interview_question(db=db, question=question)

@router.get("/job/{job_id}/categories/{category_id}", response_model=schemas.InterviewCategory)
async def read_interview_category_by_job(
    job_id: int,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get an interview category with questions specific to a job."""
    # Check if job exists
    job = crud.get_job(db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Check if category exists
    category = crud.get_interview_category(db, category_id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Interview category not found")
    
    # Get only the questions for this category and job
    questions = crud.get_interview_questions_by_category(db, category_id=category_id, job_id=job_id)
    
    # Create a response that includes only the questions for this specific job
    response = schemas.InterviewCategory(
        id=category.id,
        name=category.name,
        description=category.description,
        default_time=category.default_time,
        job_id=job_id,
        questions=questions
    )
    
    return response

@router.post("/job/{target_job_id}/clone-from/{source_job_id}", response_model=Dict[str, str])
async def clone_job_interview_structure(
    target_job_id: int,
    source_job_id: int,
    clone_questions: bool = Query(False, description="Whether to also clone the questions"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Clone interview categories from one job to another.
    Optionally clone the questions as well.
    
    This is useful when you want to reuse the same interview structure across multiple jobs,
    with either the same questions or just the same categories.
    """
    # Only HR or Hiring Manager can clone interview structures
    if current_user.role not in ["HR", "Hiring Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if source and target jobs exist
    source_job = crud.get_job(db, job_id=source_job_id)
    if source_job is None:
        raise HTTPException(status_code=404, detail="Source job not found")
        
    target_job = crud.get_job(db, job_id=target_job_id)
    if target_job is None:
        raise HTTPException(status_code=404, detail="Target job not found")
    
    # Clone the interview structure
    created_categories = crud.clone_interview_structure(
        db, 
        source_job_id=source_job_id, 
        target_job_id=target_job_id,
        clone_questions=clone_questions
    )
    
    if not created_categories:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clone interview structure"
        )
    
    return {
        "message": f"Successfully cloned {len(created_categories)} interview categories" + 
                  (" with questions" if clone_questions else " without questions")
    }

@router.put("/questions/{question_id}", response_model=schemas.InterviewQuestion)
async def update_interview_question(
    question_id: int,
    question: schemas.InterviewQuestionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Update an interview question.
    Can update text, status, must_ask flag, or change the category.
    """
    # Only HR or Hiring Manager can update questions
    if current_user.role not in ["HR", "Hiring Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if question exists
    db_question = crud.get_interview_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Interview question not found")
    
    # If updating category, check if the new category exists
    if question.category_id is not None:
        db_category = crud.get_interview_category(db, category_id=question.category_id)
        if db_category is None:
            raise HTTPException(status_code=404, detail="Interview category not found")
        
        # Make sure the new category belongs to the same job
        if db_category.job_id != db_question.job_id:
            raise HTTPException(
                status_code=400, 
                detail="Cannot move question to a category from a different job"
            )
    
    # Update the question
    updated_question = crud.update_interview_question(db, question_id=question_id, question_update=question)
    return updated_question

@router.delete("/questions/{question_id}", response_model=schemas.InterviewQuestion)
async def delete_interview_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete an interview question."""
    # Only HR or Hiring Manager can delete questions
    if current_user.role not in ["HR", "Hiring Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if question exists
    db_question = crud.get_interview_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Interview question not found")
    
    # Delete the question
    deleted_question = crud.delete_interview_question(db, question_id=question_id)
    return deleted_question

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete an interview category and all its related questions."""
    # Only HR or Hiring Manager can delete categories
    if current_user.role not in ["HR", "Hiring Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if category exists
    db_category = crud.get_interview_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Interview category not found")
    
    # Delete category and all related questions
    result = crud.delete_interview_category(db, category_id=category_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category"
        )
    
    # No content to return on successful deletion 