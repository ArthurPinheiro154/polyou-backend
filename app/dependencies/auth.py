from fastapi import Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from jwt import ExpiredSignatureError, InvalidTokenError

from ..db.crud.user import get_user_identity_by_email
from ..core.security import verify_token
from ..routes.auth import oauth2_scheme
from .session import get_db
from ..schemas.user import UserIdentity

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)])->UserIdentity:
    try:
        payload = verify_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    email = payload.get('sub')
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject"
        )
    
    user = get_user_identity_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def get_active_user(current_user: Annotated[UserIdentity, Depends(get_current_user)]) -> UserIdentity:
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inative user")
    return current_user