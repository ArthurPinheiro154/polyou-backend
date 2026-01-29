from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session

from ..schemas.user import UserIdentity
from ..schemas.flashcards import (
    FlashcardCreate, 
    FlashcardTypes, 
    RatingEnum, 
    FlashcardIdentity
)

from ..dependencies.session import get_db
from ..dependencies.auth import get_active_user
from ..db.crud.flashcards import (
    get_all_flashcards_by_user_id, 
    create_flashcard,
    get_flashcards_types,
    get_flashcard_fsrs,
    update_flashcard_fsrs,
    delete_flashcard,
    get_flashcard_info,
    update_flashcard,
)
from ..services.flashcards import (
    review_card, 
    validade_flashcard, 
    validade_flashcard_type, 
    validade_flashcard_create
)
from ..services.languages import validade_language

router = APIRouter(
    prefix="/flashcards",
    tags=['flashcards'],
    responses={404: {"description": "Not found"}}
)

@router.post("/create", response_model=list[FlashcardIdentity])
def create_flashcard_endpoint(user: Annotated[UserIdentity, Depends(get_active_user)], db: Annotated[Session, Depends(get_db)], flashcards: list[FlashcardCreate]):
    user_id = user.user_id
   
    for flashcard in flashcards:
        validade_flashcard_create(db, flashcard)
    
    responses = []
    for flashcard in flashcards:
        responses.append(create_flashcard(db, user_id, flashcard))
    
    return [FlashcardIdentity(flashcard_id=response.flashcard_id) for response in responses]

@router.get("/find", response_model=list[int])
def find_flashcard_by_id_endpoint(
    user: Annotated[UserIdentity, Depends(get_active_user)],
    db: Annotated[Session, Depends(get_db)],
    language_id: Annotated[int | None, Query()] = None,
    flashcard_type_id: Annotated[int | None, Query()] = None
):
    user_id = user.user_id
    
    if language_id:
        validade_language(db, language_id)

    if flashcard_type_id:
        validade_flashcard_type(db, flashcard_type_id)
    
    flashcards_id = get_all_flashcards_by_user_id(db, user_id, language_id, flashcard_type_id)
        
    return [flashcard_id.flashcard_id for flashcard_id in flashcards_id]

@router.get("/info")
def get_flashcard_info_endpoint(user: Annotated[UserIdentity, Depends(get_active_user)], db: Annotated[Session, Depends(get_db)], flashcard_id: int):
    user_id = user.user_id
    
    validade_flashcard(db, flashcard_id, user_id)
    
    flashcard = get_flashcard_info(db, user_id, flashcard_id)
    return flashcard

@router.put("/update")
def update_flashcard_endpoint(user: Annotated[UserIdentity, Depends(get_active_user)], db: Annotated[Session, Depends(get_db)], flashcard_id: int, new_flashcard: FlashcardCreate):
    user_id = user.user_id
    validade_flashcard(db, flashcard_id, user_id)
    validade_flashcard_create(db, new_flashcard)
    update_flashcard(db, user_id, flashcard_id, new_flashcard)        
    
@router.delete("/delete")
def delete_flashcard_endpoint(user: Annotated[UserIdentity, Depends(get_active_user)], db: Annotated[Session, Depends(get_db)], flashcard_id: int):
    user_id = user.user_id
    validade_flashcard(db, flashcard_id, user_id)
    result = delete_flashcard(db, user_id, flashcard_id)
    return result

@router.patch('/review')
def review_flashcard_endpoint(user: Annotated[UserIdentity, Depends(get_active_user)], db: Annotated[Session, Depends(get_db)], flashcard_id: int, rating: RatingEnum):
    user_id = user.user_id
    validade_flashcard(db, flashcard_id, user_id)
    flashcard_fsrs = get_flashcard_fsrs(db, flashcard_id, user_id)
   
    updated_flashcard = review_card(flashcard_fsrs, rating)

    update_flashcard_fsrs(db, user_id, flashcard_id, updated_flashcard)

    return updated_flashcard

@router.get('/types', response_model=list[FlashcardTypes])
def get_flashcard_types_endpoint(db: Annotated[Session, Depends(get_db)]):
    flashcard_types = get_flashcards_types(db)
    return flashcard_types