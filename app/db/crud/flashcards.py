from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
import datetime

from ...schemas.flashcards import (
    FlashcardIdentity,
    FlashcardCreate, 
    FlashcardTypes, 
    FlashcardReviewFSRS,
    FlashcardInfo,
    FlashcardImages,
    FlashcardContent,
    FlashcardImageIdentity
)

from ...db.models import (
    FlashcardModel,
    FlashcardContentModel,
    FlashcardFSRSModel,
    FlashcardsStatisticsModel,
    FlashcardImagesModel,
    FSRSStates,
    FlashcardTypeModel
)

def create_flashcard(db: Session, user_id: int, flashcard_create: FlashcardCreate) -> FlashcardModel:
    content = FlashcardContentModel(
        front_field_content=flashcard_create.content.front_field,
        back_field_content=flashcard_create.content.back_field,
    )

    fsrs = FlashcardFSRSModel(
        stability=0.1,
        difficulty=5.0,
        due=datetime.datetime.now(datetime.timezone.utc),
        last_review=None,
        state=FSRSStates.LEARNING,
    )

    statistics = FlashcardsStatisticsModel(
        repetitions=0,
        lapses=0,
    )

    flashcard = FlashcardModel(
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
                FlashcardImagesModel(
                    field=image_schema.field,
                    image_url=image_schema.image_url,
                )
            )

    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)
    return flashcard


def get_all_flashcards_by_user_id(db: Session, user_id: int, language_id: int | None = None, flashcard_type_id: int | None = None) -> list[FlashcardIdentity]:
    stmt = select(FlashcardModel).where(FlashcardModel.user_id == user_id)

    if language_id:
        stmt = stmt.where(FlashcardModel.language_id == language_id)

    if flashcard_type_id:
        stmt.where(FlashcardModel.flashcard_type_id == flashcard_type_id)

    flashcards = db.execute(stmt).scalars().all()

    return [
        FlashcardIdentity(flashcard_id=flashcard.flashcard_id) 
        for flashcard in flashcards
    ]

def get_flashcards_types(db: Session) -> list[FlashcardTypes]:
    stmt = select(FlashcardTypeModel)
    
    flashcards_types = db.execute(stmt).scalars().all()

    return [
        FlashcardTypes(
            flashcard_type_id=flashcard_types.flashcard_type_id,
            description=flashcard_types.description,
            type=flashcard_types.type
        ) 
        for flashcard_types in flashcards_types
    ]

def get_flashcard_fsrs(db: Session, flashcard_id: int, user_id: int) -> FlashcardReviewFSRS | None:
    stmt = select(FlashcardFSRSModel).join(FlashcardModel).where(FlashcardFSRSModel.flashcard_id == flashcard_id, FlashcardModel.user_id == user_id)
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
    subquery = select(FlashcardModel.flashcard_id).where(FlashcardModel.flashcard_id == flashcard_id, FlashcardModel.user_id == user_id)
    stmt = update(FlashcardFSRSModel).where(FlashcardFSRSModel.flashcard_id.in_(subquery)).values(**new_flashcard_fsrs.model_dump())

    try:
        result = db.execute(stmt)
        db.commit()
        return result.rowcount == 1
    except Exception:
        db.rollback()
        raise
    

def delete_flashcard(db: Session, user_id: int, flashcard_id:int) -> FlashcardIdentity:
    stmt = delete(FlashcardModel).where(FlashcardModel.user_id == user_id, FlashcardModel.flashcard_id == flashcard_id)
    try:
        db.execute(stmt)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return FlashcardIdentity(flashcard_id=flashcard_id)

def get_flashcard_info(db: Session, user_id: int, flashcard_id: int)->FlashcardInfo | None:
    stmt = select(FlashcardModel).where(FlashcardModel.user_id == user_id, FlashcardModel.flashcard_id == flashcard_id)
    flashcard = db.execute(stmt).scalar_one_or_none()

    if not flashcard:
        return None
    
    images = [FlashcardImages(field=image.field, image_url=image.image_url) for image in flashcard.images]

    content = FlashcardContent(front_field=flashcard.content.front_field_content, back_field=flashcard.content.back_field_content)

    return FlashcardInfo(
        flashcard_id=flashcard.flashcard_id,
        flashcard_type_id=flashcard.flashcard_type_id,
        images= images,
        content=content
    )

def get_flashcard_images_ids_by_flashcard_id(db: Session, flashcard_id: int, user_id: int) -> list[FlashcardImageIdentity]:
    stmt = select(FlashcardImagesModel).join(FlashcardModel).where(FlashcardImagesModel.flashcard_id == flashcard_id, FlashcardModel.user_id == user_id)
    results = db.execute(stmt).scalars().all()
    
    return [
        FlashcardImageIdentity(image_id=result.image_id)
        for result in results
    ]

def delete_flashcard_image_by_image_id(db: Session, image_id: int, user_id: int):
    subquerry = select(FlashcardModel.flashcard_id).where(FlashcardModel.user_id == user_id)
    stmt = delete(FlashcardImagesModel).where(FlashcardImagesModel.image_id == image_id, FlashcardImagesModel.flashcard_id.in_(subquerry))
    
    try:
        deleted_image_id = db.execute(stmt).scalar_one_or_none()
        db.commit()
    except Exception:
        db.rollback()
        raise

def update_flashcard(db: Session, user_id: int, flashcard_id: int, new_flashcard: FlashcardCreate) -> bool:
    try:
        flashcard: FlashcardModel | None = (
            db.query(FlashcardModel)
            .filter(
                FlashcardModel.flashcard_id == flashcard_id,
                FlashcardModel.user_id == user_id
            )
            .one_or_none()
        )

        if flashcard is None:
            return False

        flashcard.language_id = new_flashcard.language_id
        flashcard.flashcard_type_id = new_flashcard.flashcard_type_id

        flashcard.content.front_field_content = new_flashcard.content.front_field
        flashcard.content.back_field_content = new_flashcard.content.back_field

        flashcard.images.clear()

        if new_flashcard.images:
            for image in new_flashcard.images:
                flashcard.images.append(
                    FlashcardImagesModel(
                        field=image.field,
                        image_url=image.image_url
                    )
                )

        db.commit()
        return True

    except Exception:
        db.rollback()
        raise