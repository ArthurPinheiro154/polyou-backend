from pwdlib import PasswordHash
from datetime import timedelta, datetime, timezone
import jwt

from ..core.config import settings
from ..schemas.tokens import Token

password_hash = PasswordHash.recommended()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

def verify_password_hash(password: str, hash: str):
    return password_hash.verify(password, hash)

def create_access_token(data: dict, expire_delta: timedelta | None = None) -> Token:
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.now(tz=timezone.utc) + expire_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def hash_password(password: str):
    return password_hash.hash(password)