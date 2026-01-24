from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
import datetime

from ...schemas.flashcards import FlashcardIdentity, FlashcardCreate, FlashcardTypes, FlashcardReviewFSRS
from ...db.models import (
    Flashcard,
    FlashcardContent,
    FlashcardFSRS,
    FlashcardsStatistics,
    FlashcardsImages,
    FSRSStates,
    FlashcardType
)

def create_flashcard(db: Session, user_id: int, flashcard_create: FlashcardCreate) -> Flashcard:
    content = FlashcardContent(
        front_field_content=flashcard_create.content.front_field,
        back_field_content=flashcard_create.content.back_field,
    )

    fsrs = FlashcardFSRS(
        stability=0.1,
        difficulty=5.0,
        due=datetime.datetime.now(datetime.timezone.utc),
        last_review=None,
        state=FSRSStates.LEARNING,
    )

    statistics = FlashcardsStatistics(
        repetitions=0,
        lapses=0,
    )

    flashcard = Flashcard(
        user_id=user_id,
        language_id=flashcard_create.language_id,
        flashcard_type_id=flashcard_create.flashcard_type_id,
        content=content,
        fsrs=fsrs,
        statistics=statistics,
    )

    if flashcard_create.images:
        for image_schema in flashcard_create.images:
            flashcard.images.append(
                FlashcardsImages(
                    field=image_schema.field,
                    image_url=image_schema.image_url,
                )
            )

    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)
    return flashcard


def get_all_flashcards_by_user_id(db: Session, user_id: int, language_id: int | None = None, flashcard_type_id: int | None = None) -> list[FlashcardIdentity]:
    stmt = select(Flashcard).where(Flashcard.user_id == user_id)

    if language_id:
        stmt = stmt.where(Flashcard.language_id == language_id)

    if flashcard_type_id:
        stmt.where(Flashcard.flashcard_type_id == flashcard_type_id)

    flashcards = db.execute(stmt).scalars().all()

    return [
        FlashcardIdentity(flashcard_id=flashcard.flashcard_id) 
        for flashcard in flashcards
    ]

def get_flashcards_types(db: Session) -> list[FlashcardTypes]:
    stmt = select(FlashcardType)
    
    flashcards_types = db.execute(stmt).scalars().all()

    return [
        FlashcardTypes(
            flashcard_type_id=flashcard_types.flashcard_type_id,
            description=flashcard_types.description,
            type=flashcard_types.type
        ) 
        for flashcard_types in flashcards_types
    ]

def get_flashcard_fsrs(db: Session, flashcard_id: int, user_id: int) -> FlashcardFSRS | None:
    stmt = select(FlashcardFSRS).join(Flashcard).where(FlashcardFSRS.flashcard_id == flashcard_id, Flashcard.user_id == user_id)
    flashcard_fsrs = db.execute(stmt).scalar_one_or_none()

    if flashcard_fsrs is None:
        return None

    return FlashcardReviewFSRS(
        stability= flashcard_fsrs.stability, 
        difficulty=flashcard_fsrs.difficulty,
        due=flashcard_fsrs.due,
        last_review=flashcard_fsrs.last_review,
        state=flashcard_fsrs.state
    )

def update_flashcard_fsrs(db: Session, user_id:int, flashcard_id: int, new_flashcard_fsrs: FlashcardReviewFSRS) -> bool:
    subquery = select(Flashcard.flashcard_id).where(Flashcard.flashcard_id == flashcard_id, Flashcard.user_id == user_id)
    stmt = update(FlashcardFSRS).where(FlashcardFSRS.flashcard_id.in_(subquery)).values(**new_flashcard_fsrs.model_dump())

    try:
        result = db.execute(stmt)
        db.commit()
        return result.rowcount == 1
    except Exception:
        db.rollback()
        raise
    

def delete_flashcard(db: Session, user_id: int, flashcard_id:int) -> FlashcardIdentity:
    stmt = delete(Flashcard).where(Flashcard.user_id == user_id, Flashcard.flashcard_id == flashcard_id)
    try:
        db.execute(stmt)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return FlashcardIdentity(flashcard_id=flashcard_id)