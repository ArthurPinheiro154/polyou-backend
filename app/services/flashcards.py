from fsrs import Scheduler, Card, Rating, State
from datetime import datetime, timedelta, timezone

from ..schemas.flashcards import FlashcardReviewFSRS, StateEnum, RatingEnum
from ..core.utc_safe import utcnow
from ..core.config import DEFAULT_FSRS_CONFIG

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