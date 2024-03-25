from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from app import oauth2
from app.schemas.user import UserOut, UserCreate
from app.models.user import User
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils import hashed

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    if db.query(User).filter_by(email=user.email).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User with email {user.email} already exist")

    # hash the password - user.password
    hashed_password = hashed(user.password)
    user.password = hashed_password

    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/infos", response_model=UserOut)
async def get_user_infos(current_user: Annotated[User, Depends(oauth2.get_current_user)]):
    return current_user

@router.get("/{id}", response_model=UserOut)
async def get_user(id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter_by(id=id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} does not exists")

    return user
