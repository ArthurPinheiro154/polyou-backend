from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

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
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3

class RatingEnum(int, Enum):
    AGAIN = 1
    HARD = 2
    GOOD = 3

class FlashcardInfo(BaseModel):
    flashcard_id: int
    flashcard_type_id: int
    images: list[FlashcardImages] | None = None
    content: FlashcardContent

class FlashcardReviewFSRS(BaseModel):
    stability: float = 0.1
    difficulty: float = 5.0
    due: datetime = Field(default_factory=datetime.today)
    last_review: datetime | None = None
    state: StateEnum = StateEnum.LEARNING

class FlashcardCreate(BaseModel):
    language_id: int
    flashcard_type_id: int

    images: list[FlashcardImages] | None = None
    content: FlashcardContent


class FlashcardIdentity(BaseModel):
    flashcard_id: int

class FlashcardImageIdentity(BaseModel):
    image_id: int