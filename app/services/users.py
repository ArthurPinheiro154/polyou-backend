from sqlalchemy.orm import Session

from ..db.crud.user import get_user_credentials_by_email
from ..schemas.user import UserRegisterInformation, UserCreate, UserCredentials
from ..core.security import hash_password

def build_user_create(user_register_information: UserRegisterInformation) -> UserCreate:
    password = user_register_information.credentials.password
    hashed_password = hash_password(password)
    return UserCreate(
        credentials= UserCredentials(
            email = user_register_information.credentials.email,
            hashed_password= hashed_password
        ),
        profile = user_register_information.profile,
        known_languages= user_register_information.known_languages,
        target_languages= user_register_information.target_languages
    )

def email_exists(db: Session, email:str) -> bool:
    user = get_user_credentials_by_email(db, email)
    if not user:
        return False
    return True