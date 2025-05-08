from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .. import schemas, crud, models, auth
from ..database import get_db

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])

@router.post("", response_model=schemas.Candidate)
async def create_candidate(
    candidate: schemas.CandidateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a new candidate for a job."""
    # Only HR or Hiring Manager can create candidates
    if current_user.role not in ["HR", "Hiring Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if job exists
    job = crud.get_job(db, job_id=candidate.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return crud.create_candidate(db=db, candidate=candidate)

@router.get("/job/{job_id}", response_model=List[schemas.Candidate])
async def read_candidates_by_job(
    job_id: int,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[int] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    max_rating: Optional[float] = Query(None, ge=0, le=5),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all candidates for a specific job with optional filters.
    status: Integer (0: Screening, 1: Interview, 2: Hired, 3: Rejected)
    """
    # Check if job exists
    job = crud.get_job(db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    candidates = crud.search_candidates(
        db,
        job_id=job_id,
        search_term=search,
        status=status,
        min_rating=min_rating,
        max_rating=max_rating,
        skip=skip,
        limit=limit
    )
    return candidates

@router.get("/{candidate_id}", response_model=schemas.Candidate)
async def read_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get a specific candidate by ID."""
    candidate = crud.get_candidate(db, candidate_id=candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.put("/{candidate_id}", response_model=schemas.Candidate)
async def update_candidate(
    candidate_id: int,
    candidate: schemas.CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update a candidate's information."""
    # Only HR or Hiring Manager can update candidates
    if current_user.role not in ["HR", "Hiring Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if candidate exists
    db_candidate = crud.get_candidate(db, candidate_id=candidate_id)
    if db_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    updated_candidate = crud.update_candidate(db, candidate_id=candidate_id, candidate_update=candidate)
    return updated_candidate

@router.delete("/{candidate_id}", response_model=schemas.Candidate)
async def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete a candidate."""
    # Only HR or Hiring Manager can delete candidates
    if current_user.role not in ["HR", "Hiring Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if candidate exists
    candidate = crud.get_candidate(db, candidate_id=candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    deleted_candidate = crud.delete_candidate(db, candidate_id=candidate_id)
    return deleted_candidate

@router.post("/bulk-status-update", response_model=List[schemas.Candidate])
async def bulk_update_candidate_status(
    candidate_ids: List[int],
    new_status: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Update status for multiple candidates at once.
    new_status: Integer (0: Screening, 1: Interview, 2: Hired, 3: Rejected)
    """
    # Only HR or Hiring Manager can update candidates
    if current_user.role not in ["HR", "Hiring Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate status value
    if new_status not in [0, 1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status value. Must be 0, 1, 2, or 3."
        )
    
    updated_candidates = []
    for candidate_id in candidate_ids:
        # Check if candidate exists
        db_candidate = crud.get_candidate(db, candidate_id=candidate_id)
        if db_candidate:
            # Update only the status
            updated_candidate = crud.update_candidate(
                db, 
                candidate_id=candidate_id, 
                candidate_update=schemas.CandidateUpdate(status=new_status)
            )
            updated_candidates.append(updated_candidate)
    
    return updated_candidates

@router.get("/job/{job_id}/status/{status_value}", response_model=List[schemas.Candidate])
async def get_candidates_by_status(
    job_id: int,
    status_value: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get candidates filtered by job and status.
    status_value: Integer (0: Screening, 1: Interview, 2: Hired, 3: Rejected)
    """
    # Check if job exists
    job = crud.get_job(db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Validate status value
    if status_value not in [0, 1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status value. Must be 0, 1, 2, or 3."
        )
    
    candidates = crud.search_candidates(
        db,
        job_id=job_id,
        status=status_value,
        skip=skip,
        limit=limit
    )
    return candidates

@router.get("/job/{job_id}/status-counts")
async def get_candidate_status_counts(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get the count of candidates for each status for a specific job.
    Returns counts for each status:
    {
        "0": 5,  # 5 candidates in Screening
        "1": 3,  # 3 candidates in Interview
        "2": 1,  # 1 candidate Hired
        "3": 2,  # 2 candidates Rejected
        "total": 11
    }
    """
    # Check if job exists
    job = crud.get_job(db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return crud.get_candidate_status_counts(db, job_id=job_id) 