from pydantic import BaseModel, Field
from enum import Enum
from datetime import date


class FlashcardTypes(BaseModel):
    flashcard_type_id: int
    type: str
    description: str | None = None


class FieldsEnum(str, Enum):
    front = "front"
    back = "back"


class FlashcardImages(BaseModel):
    field: FieldsEnum
    image_url: str


class FlashcardContent(BaseModel):
    front_field: str
    back_field: str | None = None


class StateEnum(int, Enum):
    NEW = 0
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3


class FlashcardReviewFSRS(BaseModel):
    stability: float = 0.0
    difficulty: float = 5.0
    due: date = Field(default_factory=date.today)
    last_review: date | None = None
    state: StateEnum = StateEnum.NEW


class FlashcardCreate(BaseModel):
    language_id: int
    flashcard_type_id: int

    images: list[FlashcardImages] | None = None
    content: FlashcardContent


class FlashcardIdentity(BaseModel):
    flashcard_id: int
