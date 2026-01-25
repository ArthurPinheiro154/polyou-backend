from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import EmailStr

from ...schemas.user import UserCreate, UserCredentials, UserIdentity
from ...db.models import UserModel, UserProfileModel, UserKnownLanguageModel, UserTargetLanguageModel

def create_user(db: Session, user_create: UserCreate) -> UserModel:
    user = UserModel(
        **user_create.credentials.model_dump(),
        profile = UserProfileModel(**user_create.profile.model_dump()),
        known_languages = [
            UserKnownLanguageModel(**lang.model_dump()) for lang in user_create.known_languages
        ],
        target_languages = [
            UserTargetLanguageModel(**lang.model_dump()) for lang in user_create.target_languages
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
    stmt = select(UserModel).where(UserModel.email == email)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        return None

    return UserCredentials(
        email=user.email,
        hashed_password=user.hashed_password
    )

def get_user_identity_by_email(db: Session, email: EmailStr) -> UserIdentity | None:
    stmt = select(UserModel).where(UserModel.email == email)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        return None
    
    return UserIdentity(
        user_id=user.user_id,
        disabled=user.disabled
    )