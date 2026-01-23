from sqlalchemy.orm import Session
from sqlalchemy import select

from ...schemas.flashcards import FlashcardIdentity, FlashcardCreate, FlashcardTypes
from ...db.models import Flashcard, FlashcardType

from sqlalchemy.orm import Session
import datetime

from ...db.models import (
    Flashcard,
    FlashcardContent,
    FlashcardReviewFSRS,
    FlashcardsStatistics,
    FlashcardsImages,
    FSRSStates,
)

def create_flashcard(db: Session, user_id: int, flashcard_create: FlashcardCreate) -> Flashcard:
    content = FlashcardContent(
        front_field_content=flashcard_create.content.front_field,
        back_field_content=flashcard_create.content.back_field,
    )

    fsrs = FlashcardReviewFSRS(
        stability=0.0,
        difficulty=5.0,
        due=datetime.datetime.now(datetime.timezone.utc),
        last_review=None,
        state=FSRSStates.NEW,
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