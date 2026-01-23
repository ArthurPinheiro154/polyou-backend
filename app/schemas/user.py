from pydantic import BaseModel, EmailStr
from datetime import date
from .languages import KnownLanguageCreate, TargetLanguagesCreate

class UserIdentity(BaseModel):
    user_id: int
    disabled: bool
    
class UserCredentials(BaseModel):
    email: EmailStr
    hashed_password: str

class UserProfile(BaseModel):
    first_name: str
    last_name: str
    birth: date | None = None

class UserLoginCredentials(BaseModel):
    email: EmailStr
    password: str

class UserRegisterInformation(BaseModel):
    credentials: UserLoginCredentials
    profile: UserProfile
    known_languages: list[KnownLanguageCreate]
    target_languages: list[TargetLanguagesCreate]

class UserCreate(BaseModel):
    credentials: UserCredentials
    profile: UserProfile
    known_languages: list[KnownLanguageCreate]
    target_languages: list[TargetLanguagesCreate]

