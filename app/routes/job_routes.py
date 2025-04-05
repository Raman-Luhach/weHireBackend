from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas, crud, models, auth
from ..database import get_db

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("/", response_model=schemas.Job)
async def create_job(
    job: schemas.JobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Check if assigned hiring manager exists (if provided)
    if job.assigned_to:
        assigned_manager = crud.get_user(db, user_id=job.assigned_to)
        if not assigned_manager or assigned_manager.role != "Hiring Manager":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid hiring manager ID"
            )
    
    return crud.create_job(db=db, job=job)

@router.get("/", response_model=List[schemas.Job])
async def read_jobs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by job status"),
    title: Optional[str] = Query(None, description="Filter by job title"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    jobs = crud.get_jobs(db, skip=skip, limit=limit, status=status, title=title)
    return jobs

@router.get("/manager/{manager_id}", response_model=List[schemas.Job])
async def read_jobs_by_manager(
    manager_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all jobs assigned to a specific manager.
    This can be used after a hiring manager signs in to show only their assigned jobs.
    """
    # Check if the manager exists
    manager = crud.get_user(db, user_id=manager_id)
    if not manager or manager.role != "Hiring Manager":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hiring manager not found"
        )
    
    # Get jobs for this manager
    jobs = crud.get_jobs_by_manager(db, manager_id=manager_id, skip=skip, limit=limit)
    return jobs

@router.get("/{job_id}", response_model=schemas.JobDetail)
async def read_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@router.put("/{job_id}", response_model=schemas.Job)
async def update_job(
    job_id: int,
    job: schemas.JobUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if assigned hiring manager exists (if provided)
    if job.assigned_to:
        assigned_manager = crud.get_user(db, user_id=job.assigned_to)
        if not assigned_manager or assigned_manager.role != "Hiring Manager":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid hiring manager ID"
            )
    
    updated_job = crud.update_job(db=db, job_id=job_id, job_update=job)
    return updated_job

@router.delete("/{job_id}", response_model=schemas.Job)
async def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Additional permission check could be added here
    # For example, only HR can delete jobs
    if current_user.role != "HR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR can delete jobs"
        )
    
    return crud.delete_job(db=db, job_id=job_id) 