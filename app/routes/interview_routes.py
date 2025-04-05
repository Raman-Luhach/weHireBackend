from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

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
    
    return crud.create_interview_question(db=db, question=question) 