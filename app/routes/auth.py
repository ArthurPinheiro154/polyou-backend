from datetime import timedelta
from typing import Annotated

from fastapi import HTTPException, Depends, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from ..schemas.user import UserLoginCredentials
from ..schemas.tokens import Token

from ..dependencies.session import get_db
from ..services.auth import authenticate_user
from ..core.security import create_access_token

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix="/auth",
    tags=['auth'],
    responses={404: {"description": "Not found"}}
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.post("/token", tags=['auth'])
def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]) -> Token:
    user = authenticate_user(db, UserLoginCredentials(email=form_data.username, password=form_data.password))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"sub": user.email}, 
        expire_delta = access_token_expire
    )
    
    return Token(access_token=access_token, token_type='bearer')