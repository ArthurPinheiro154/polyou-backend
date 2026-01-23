from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    ForeignKey,
    SmallInteger,
    DateTime,
    Date,
    Boolean,
    func,
    Enum as SQLEnum,
)
import datetime
from typing import List, Optional
from enum import Enum


# =========================================================
# Base
# =========================================================

class PolyouDB(DeclarativeBase):
    pass


# =========================================================
# Users
# =========================================================

class User(PolyouDB):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    known_languages: Mapped[List["UserKnownLanguage"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    target_languages: Mapped[List["UserTargetLanguage"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    flashcards: Mapped[List["Flashcard"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class UserProfile(PolyouDB):
    __tablename__ = "users_profile"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        primary_key=True
    )

    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    birth: Mapped[Optional[datetime.date]] = mapped_column(Date)

    user: Mapped["User"] = relationship(back_populates="profile")


# =========================================================
# Languages
# =========================================================

class Language(PolyouDB):
    __tablename__ = "languages"

    language_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    iso_639_1: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)

    known_by_users: Mapped[List["UserKnownLanguage"]] = relationship(back_populates="language")
    target_by_users: Mapped[List["UserTargetLanguage"]] = relationship(back_populates="language")
    flashcards: Mapped[List["Flashcard"]] = relationship(back_populates="language")


class UserKnownLanguage(PolyouDB):
    __tablename__ = "user_known_languages"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        primary_key=True
    )

    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.language_id"),
        primary_key=True
    )

    user: Mapped["User"] = relationship(back_populates="known_languages")
    language: Mapped["Language"] = relationship(back_populates="known_by_users")


# =========================================================
# Target Languages / Goals / Levels
# =========================================================

class CEFRLevel(PolyouDB):
    __tablename__ = "cefr_levels"

    level_id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)

    user_targets: Mapped[List["UserTargetLanguage"]] = relationship(back_populates="level")


class Goal(PolyouDB):
    __tablename__ = "goals"

    goal_id: Mapped[int] = mapped_column(primary_key=True)
    goal: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    user_targets: Mapped[List["UserTargetLanguage"]] = relationship(back_populates="goal")


class UserTargetLanguage(PolyouDB):
    __tablename__ = "user_target_languages"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        primary_key=True
    )

    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.language_id"),
        primary_key=True
    )

    level_id: Mapped[int] = mapped_column(ForeignKey("cefr_levels.level_id"), nullable=False)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.goal_id"), nullable=False)

    priority: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    user: Mapped["User"] = relationship(back_populates="target_languages")
    language: Mapped["Language"] = relationship(back_populates="target_by_users")
    level: Mapped["CEFRLevel"] = relationship(back_populates="user_targets")
    goal: Mapped["Goal"] = relationship(back_populates="user_targets")


# =========================================================
# Flashcards
# =========================================================

class Fields(Enum):
    front = "front"
    back = "back"


class FlashcardType(PolyouDB):
    __tablename__ = "flashcard_types"

    flashcard_type_id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)

    flashcards: Mapped[List["Flashcard"]] = relationship(back_populates="flashcard_type")


class Flashcard(PolyouDB):
    __tablename__ = "flashcards"

    flashcard_id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.language_id"), nullable=False)
    flashcard_type_id: Mapped[int] = mapped_column(
        ForeignKey("flashcard_types.flashcard_type_id"),
        nullable=False
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="flashcards")
    language: Mapped["Language"] = relationship(back_populates="flashcards")
    flashcard_type: Mapped["FlashcardType"] = relationship(back_populates="flashcards")

    content: Mapped["FlashcardContent"] = relationship(
        back_populates="flashcard",
        uselist=False,
        cascade="all, delete-orphan"
    )

    fsrs: Mapped["FlashcardReviewFSRS"] = relationship(
        back_populates="flashcard",
        uselist=False,
        cascade="all, delete-orphan"
    )

    statistics: Mapped["FlashcardsStatistics"] = relationship(
        back_populates="flashcard",
        uselist=False,
        cascade="all, delete-orphan"
    )

    images: Mapped[List["FlashcardsImages"]] = relationship(
        back_populates="flashcard",
        cascade="all, delete-orphan"
    )

class FlashcardContent(PolyouDB):
    __tablename__ = "flashcards_content"

    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.flashcard_id"),
        primary_key=True
    )

    front_field_content: Mapped[str] = mapped_column(String, nullable=False)
    back_field_content: Mapped[Optional[str]] = mapped_column(String)

    flashcard: Mapped["Flashcard"] = relationship(back_populates="content")


# =========================================================
# FSRS
# =========================================================

class FSRSStates(Enum):
    NEW = 0
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3


class FlashcardReviewFSRS(PolyouDB):
    __tablename__ = "flashcards_review_fsrs"

    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.flashcard_id"),
        primary_key=True
    )

    stability: Mapped[float] = mapped_column(nullable=False)
    difficulty: Mapped[float] = mapped_column(nullable=False)

    due: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_review: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    state: Mapped[FSRSStates] = mapped_column(
        SQLEnum(FSRSStates),
        nullable=False
    )

    flashcard: Mapped["Flashcard"] = relationship(back_populates="fsrs")


class FlashcardsStatistics(PolyouDB):
    __tablename__ = "flashcards_statistics"

    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.flashcard_id"),
        primary_key=True
    )

    repetitions: Mapped[int] = mapped_column(nullable=False, default=0)
    lapses: Mapped[int] = mapped_column(nullable=False, default=0)

    flashcard: Mapped["Flashcard"] = relationship(back_populates="statistics")

# =========================================================
# Images
# =========================================================

class FlashcardsImages(PolyouDB):
    __tablename__ = "flashcards_images"

    image_id: Mapped[int] = mapped_column(primary_key=True)

    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.flashcard_id"),
        nullable=False
    )

    field: Mapped[Fields] = mapped_column(SQLEnum(Fields), nullable=False)

    image_url: Mapped[str] = mapped_column(String, nullable=False)

    flashcard: Mapped["Flashcard"] = relationship(back_populates="images")

# =========================================================
# Create / Drop (opcional)
# =========================================================

#from connection import engine
#PolyouDB.metadata.create_all(engine)
#PolyouDB.metadata.drop_all(engine)