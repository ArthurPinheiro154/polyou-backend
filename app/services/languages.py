from ..db.crud.languages import get_language_by_id
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

def language_exists(db: Session, language_id: int) -> bool:
    language = get_language_by_id(db, language_id)

    if language:
        return True
    
    return False

def validade_language(db: Session, language_id: int):
    if not language_exists(db, language_id):
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"The language id '{language_id}' do not exist. You can get all available languages by the route '/languages'."
        )