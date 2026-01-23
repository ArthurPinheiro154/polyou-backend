from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session

from ..schemas.user import UserIdentity
from ..schemas.flashcards import FlashcardCreate
from ..db.session import get_db
from ..dependencies.auth import get_active_user
from ..db.crud.flashcards import get_all_flashcards_by_user_id, create_flashcard

router = APIRouter(
    prefix="/flashcards",
    tags=['flashcards'],
    responses={404: {"description": "Not found"}}
)

@router.post("/create")
def create_flashcard_endpoint(
    user: Annotated[UserIdentity, Depends(get_active_user)],
    db: Annotated[Session, Depends(get_db)],
    flashcards: list[FlashcardCreate]
):
    user_id = user.user_id
    for flashcard in flashcards:
        create_flashcard(db, user_id, flashcard)

@router.put("/update")
def update_flashcard_endpoint():
    pass

@router.get("/find", response_model=list[int])
def find_flashcard_by_id_endpoint(
    user: Annotated[UserIdentity, Depends(get_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    user_id = user.user_id
    flashcards_id = get_all_flashcards_by_user_id(db, user_id)
    
    return [flashcard_id.flashcard_id for flashcard_id in flashcards_id]
    
@router.get("/info")
def get_flashcard_info():
    pass

@router.delete("/delete")
def delete_flashcard():
    pass