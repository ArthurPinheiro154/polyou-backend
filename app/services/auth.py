from sqlalchemy.orm import Session

from ..schemas.user import UserLoginCredentials, UserCredentials
from ..db.crud.user import get_user_credentials_by_email
from ..core.security import verify_password_hash

def authenticate_user(db: Session, user_login_credentials:UserLoginCredentials) -> UserCredentials | None:
    user_credentials = get_user_credentials_by_email(db, user_login_credentials.email)
    
    if not user_credentials:
        return None
    
    if not verify_password_hash(user_login_credentials.password, user_credentials.hashed_password):
        return None
    
    return user_credentials