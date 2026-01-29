from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session

from ..db.crud.user import create_user
from ..dependencies.session import get_db
from ..schemas.user import UserRegisterInformation, UserIdentity
from ..schemas.tokens import Token
from ..services.users import build_user_create, email_exists
from ..core.security import create_access_token

from ..dependencies.auth import get_active_user

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {"description": "Not found"}}
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user_endpoint(db: Annotated[Session, Depends(get_db)], user_register_information: UserRegisterInformation):
    if email_exists(db, user_register_information.credentials.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Email already registered.'
        )
    user_create = build_user_create(user_register_information)
    create_user(db, user_create)

    access_token = create_access_token(
        data={
            "sub": user_create.credentials.email
        }
    )

    return Token(access_token=access_token, token_type='bearer')

@router.get("/me", response_model=UserIdentity)
def read_users_me(current_user: Annotated[UserIdentity, Depends(get_active_user)]):
    return current_user