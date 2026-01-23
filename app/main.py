from fastapi import FastAPI
from .core.config import settings
from .routes import auth, users, languages, flashcards

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(languages.router)
app.include_router(flashcards.router)