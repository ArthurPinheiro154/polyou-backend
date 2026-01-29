from fastapi import HTTPException, status

from fsrs import Scheduler, Card, Rating, State
from sqlalchemy.orm import Session

from ..schemas.flashcards import FlashcardReviewFSRS, StateEnum, RatingEnum, FlashcardCreate
from ..core.utc_safe import utcnow
from ..core.config import DEFAULT_FSRS_CONFIG
from ..db.crud.flashcards import get_flashcard_by_id, get_flashcard_by_id_and_user_id, get_flashcard_type_by_id
from ..services.languages import validade_language

scheduler = Scheduler(desired_retention=DEFAULT_FSRS_CONFIG.DESIRED_RETENTION)

def map_rating(rating: RatingEnum) -> Rating:
    return {
        RatingEnum.AGAIN: Rating.Again,
        RatingEnum.HARD: Rating.Hard,
        RatingEnum.GOOD: Rating.Good
    }[rating]

FSRS_STATE_MAP = {
    StateEnum.LEARNING: State.Learning,
    StateEnum.REVIEW: State.Review,
    StateEnum.RELEARNING: State.Relearning,
}

REVERSE_STATE_MAP = {v: k for k, v in FSRS_STATE_MAP.items()}

def review_card(old_flashcard: FlashcardReviewFSRS, rating: RatingEnum) -> FlashcardReviewFSRS:
    now = utcnow()

    if old_flashcard.state == StateEnum.LEARNING:
        stability = max(old_flashcard.stability, DEFAULT_FSRS_CONFIG.LEARNING_MIN_STABILITY)
        due = now + DEFAULT_FSRS_CONFIG.MINIMUM_REVIEW_INTERVAL
        
        if rating == RatingEnum.AGAIN:
            state = StateEnum.LEARNING 
        else:
            stability += DEFAULT_FSRS_CONFIG.LEARNING_STABILITY_INCREMENT 
            state = StateEnum.REVIEW
        
        return FlashcardReviewFSRS(
            stability=stability,
            difficulty=old_flashcard.difficulty,
            due=due,
            state=state,
            last_review=now
        )

    card = Card(
        state=FSRS_STATE_MAP[old_flashcard.state],
        stability=old_flashcard.stability,
        difficulty=old_flashcard.difficulty,
        due=old_flashcard.due,
        last_review=old_flashcard.last_review or now,
    )

    fsrs_rating = map_rating(rating)

    updated_card, _ = scheduler.review_card(card, fsrs_rating, now)
    
    if updated_card.due.date() <= now.date():
        updated_card.due = (now + DEFAULT_FSRS_CONFIG.MINIMUM_REVIEW_INTERVAL).replace(hour=0, minutes=0, second=0, microsecond=0)

    return FlashcardReviewFSRS(
        stability=updated_card.stability,
        difficulty=updated_card.difficulty,
        due=updated_card.due,
        last_review=updated_card.last_review,
        state=REVERSE_STATE_MAP[updated_card.state],
    )

def flashcard_exists(db: Session, flashcard_id: int) -> bool:
    flashcard = get_flashcard_by_id(db, flashcard_id)
    
    if flashcard:
        return True
    
    return False

def flashcard_belongs_to_user(db: Session, flashcard_id: int, user_id: int) -> bool:
    flashcard = get_flashcard_by_id_and_user_id(db, flashcard_id, user_id)

    if flashcard:
        return True
    
    return False

def validade_flashcard(db: Session, flashcard_id: int, user_id)-> None:
    if not flashcard_exists(db, flashcard_id):
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"The flashcard ID '{flashcard_id}' do not exist."
        )

    if not flashcard_belongs_to_user(db, flashcard_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= f"The flashcard ID {flashcard_id} do not belong to the authenticated user."
        )

def flashcard_type_exists(db: Session, flashcard_type_id: int) -> bool:
    flashcard_type = get_flashcard_type_by_id(db, flashcard_type_id)

    if flashcard_type:
        return True
    
    return False

def validade_flashcard_type(db: Session, flashcard_type_id: int) -> None:
    if not flashcard_type_exists(db, flashcard_type_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = f"The flashcard type id '{flashcard_type_id}' do not exists. You can get all available flashcard types ids in the route '/flashcards/types'."
        )

def validade_flashcard_create(db: Session, flashcard_create: FlashcardCreate) -> None:
    flashcard_type_id = flashcard_create.flashcard_type_id
    language_id = flashcard_create.language_id
    
    validade_flashcard_type(db, flashcard_type_id)
    validade_language(db, language_id)