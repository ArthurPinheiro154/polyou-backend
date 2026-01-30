from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    SmallInteger,
    DateTime,
    Date,
    Boolean,
    Enum as SQLEnum,
)
from typing import List, Optional
from enum import Enum
from datetime import datetime

from ..core.utc_safe import utcnow

# =========================================================
# Base
# =========================================================
class PolyouDB(DeclarativeBase):
    pass

# =========================================================
# Enums
# =========================================================
class Fields(Enum):
    front = "front"
    back = "back"


class FSRSStates(int, Enum):
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3


# =========================================================
# Users
# =========================================================
class UserModel(PolyouDB):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    profile: Mapped["UserProfileModel"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    known_languages: Mapped[List["UserKnownLanguageModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    target_languages: Mapped[List["UserTargetLanguageModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    flashcards: Mapped[List["FlashcardModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class UserProfileModel(PolyouDB):
    __tablename__ = "users_profile"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    birth: Mapped[Optional[datetime.date]] = mapped_column(Date)

    user: Mapped["UserModel"] = relationship(back_populates="profile")


# =========================================================
# Languages
# =========================================================
class LanguageModel(PolyouDB):
    __tablename__ = "languages"

    language_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    iso_639_1: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)

    known_by_users: Mapped[List["UserKnownLanguageModel"]] = relationship(back_populates="language")
    target_by_users: Mapped[List["UserTargetLanguageModel"]] = relationship(back_populates="language")
    flashcards: Mapped[List["FlashcardModel"]] = relationship(back_populates="language")


class UserKnownLanguageModel(PolyouDB):
    __tablename__ = "user_known_languages"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.language_id", ondelete="CASCADE"),
        primary_key=True
    )

    user: Mapped["UserModel"] = relationship(back_populates="known_languages")
    language: Mapped["LanguageModel"] = relationship(back_populates="known_by_users")


# =========================================================
# Target Languages / Goals / Levels
# =========================================================
class CEFRLevelModel(PolyouDB):
    __tablename__ = "cefr_levels"

    level_id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)

    user_targets: Mapped[List["UserTargetLanguageModel"]] = relationship(back_populates="level")


class GoalModel(PolyouDB):
    __tablename__ = "goals"

    goal_id: Mapped[int] = mapped_column(primary_key=True)
    goal: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    user_targets: Mapped[List["UserTargetLanguageModel"]] = relationship(back_populates="goal")


class UserTargetLanguageModel(PolyouDB):
    __tablename__ = "user_target_languages"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.language_id", ondelete="CASCADE"),
        primary_key=True
    )
    level_id: Mapped[int] = mapped_column(ForeignKey("cefr_levels.level_id"), nullable=False)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.goal_id"), nullable=False)
    priority: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="target_languages")
    language: Mapped["LanguageModel"] = relationship(back_populates="target_by_users")
    level: Mapped["CEFRLevelModel"] = relationship(back_populates="user_targets")
    goal: Mapped["GoalModel"] = relationship(back_populates="user_targets")


# =========================================================
# Flashcards
# =========================================================
class FlashcardTypeModel(PolyouDB):
    __tablename__ = "flashcard_types"

    flashcard_type_id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)

    flashcards: Mapped[List["FlashcardModel"]] = relationship(back_populates="flashcard_type")


class FlashcardModel(PolyouDB):
    __tablename__ = "flashcards"

    flashcard_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.language_id"), nullable=False)
    flashcard_type_id: Mapped[int] = mapped_column(ForeignKey("flashcard_types.flashcard_type_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="flashcards")
    language: Mapped["LanguageModel"] = relationship(back_populates="flashcards")
    flashcard_type: Mapped["FlashcardTypeModel"] = relationship(back_populates="flashcards")

    content: Mapped["FlashcardContentModel"] = relationship(
        back_populates="flashcard",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    fsrs: Mapped["FlashcardFSRSModel"] = relationship(
        back_populates="flashcard",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    reviews: Mapped[List["FlashcardReviewModel"]] = relationship(
        back_populates="flashcard",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    images: Mapped[List["FlashcardImagesModel"]] = relationship(
        back_populates="flashcard",
        cascade="save-update, merge",
        passive_deletes=True
    )

    audios: Mapped[List["FlashcardAudiosModel"]] = relationship(
        back_populates="flashcard",
        cascade="save-update, merge",
        passive_deletes=True
    )


class FlashcardContentModel(PolyouDB):
    __tablename__ = "flashcards_content"

    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.flashcard_id", ondelete="CASCADE"),
        primary_key=True
    )
    front_field_content: Mapped[str] = mapped_column(String, nullable=False)
    back_field_content: Mapped[Optional[str]] = mapped_column(String)

    flashcard: Mapped["FlashcardModel"] = relationship(
        back_populates="content",
        passive_deletes=True
    )


class FlashcardFSRSModel(PolyouDB):
    __tablename__ = "flashcards_fsrs"

    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.flashcard_id", ondelete="CASCADE"),
        primary_key=True
    )
    stability: Mapped[float] = mapped_column(nullable=False, default=0.3)
    difficulty: Mapped[float] = mapped_column(nullable=False, default=5.0)
    due: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_review: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    state: Mapped[FSRSStates] = mapped_column(SQLEnum(FSRSStates), nullable=False, default=FSRSStates.LEARNING)

    flashcard: Mapped["FlashcardModel"] = relationship(
        back_populates="fsrs",
        passive_deletes=True
    )


class FlashcardReviewModel(PolyouDB):
    __tablename__ = "flashcards_reviews"

    review_id: Mapped[int] = mapped_column(primary_key=True)
    
    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.flashcard_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=utcnow, 
        nullable=False
    )
    
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    
    scheduled_days: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_days: Mapped[int] = mapped_column(Integer, nullable=False)
    
    prev_stability: Mapped[float] = mapped_column(nullable=False)
    prev_difficulty: Mapped[float] = mapped_column(nullable=False)
    new_stability: Mapped[float] = mapped_column(nullable=False)
    new_difficulty: Mapped[float] = mapped_column(nullable=False)
    
    state_before: Mapped[FSRSStates] = mapped_column(SQLEnum(FSRSStates), nullable=False)
    state_after: Mapped[FSRSStates] = mapped_column(SQLEnum(FSRSStates), nullable=False)

    flashcard: Mapped["FlashcardModel"] = relationship(back_populates="reviews")


class FlashcardImagesModel(PolyouDB):
    __tablename__ = "flashcards_images"

    image_id: Mapped[int] = mapped_column(primary_key=True)
    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.flashcard_id", ondelete="CASCADE"),
        nullable=False
    )
    field: Mapped[Fields] = mapped_column(SQLEnum(Fields), nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

    flashcard: Mapped["FlashcardModel"] = relationship(
        back_populates="images",
        passive_deletes=True
    )

class FlashcardAudiosModel(PolyouDB):
    __tablename__ = "flashcards_audios"

    audio_id: Mapped[int] = mapped_column(primary_key=True)
    
    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.flashcard_id", ondelete="CASCADE"),
        nullable=False
    )
    
    field: Mapped[Fields] = mapped_column(SQLEnum(Fields), nullable=False)
    audio_url: Mapped[str] = mapped_column(String, nullable=False)

    flashcard: Mapped["FlashcardModel"] = relationship(
        back_populates="images",
        passive_deletes=True
    )

# =========================================================
# Create / Drop (opcional)
# =========================================================
# from connection import engine
# PolyouDB.metadata.create_all(engine)
# PolyouDB.metadata.drop_all(engine)