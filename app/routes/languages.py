from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session

from ..schemas.languages import AvailableLanguage
from ..db.session import get_db
from ..db.crud.languages import get_available_languages

router = APIRouter(
    prefix="/languages",
    tags=['languages'],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=list[AvailableLanguage])
def get_available_language_endpoint(db:Annotated[Session, Depends(get_db)]):
    available_languages = get_available_languages(db)
    return available_languages