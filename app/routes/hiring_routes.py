from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, models, auth
from ..database import get_db

router = APIRouter(prefix="/api/hiring-managers", tags=["Hiring Managers"])

@router.get("/", response_model=List[schemas.User])
async def read_hiring_managers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    hiring_managers = crud.get_hiring_managers(db)
    return hiring_managers 