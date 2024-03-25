from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils, oauth2
from app.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import ResetPassword

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login_for_access_token(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter_by(email=user_credentials.username).first()

    if user is None or not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/reset-password")
async def reset_password(reset_request: ResetPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=reset_request.email).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found with the provided email")

    user.password = utils.hashed(reset_request.new_password)
    db.commit()

    return {"message": "Password reset successful. You can now use the new password."}



