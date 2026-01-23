from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import EmailStr

from ...schemas.user import UserCreate, UserCredentials, UserIdentity
from ...db.models import User, UserProfile, UserKnownLanguage, UserTargetLanguage

def create_user(db: Session, user_create: UserCreate) -> User:
    user = User(
        **user_create.credentials.model_dump(),
        profile = UserProfile(**user_create.profile.model_dump()),
        known_languages = [
            UserKnownLanguage(**lang.model_dump()) for lang in user_create.known_languages
        ],
        target_languages = [
            UserTargetLanguage(**lang.model_dump()) for lang in user_create.target_languages
        ]
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise

def get_user_credentials_by_email(db: Session, email: EmailStr) -> UserCredentials | None:
    stmt = select(User).where(User.email == email)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        return None

    return UserCredentials(
        email=user.email,
        hashed_password=user.hashed_password
    )

def get_user_identity_by_email(db: Session, email: EmailStr) -> UserIdentity | None:
    stmt = select(User).where(User.email == email)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        return None
    
    return UserIdentity(
        user_id=user.user_id,
        disabled=user.disabled
    )
    