from pydantic import BaseModel

class TargetLanguagesCreate(BaseModel):
    language_id: int
    level_id: int
    goal_id: int
    priority: int

class KnownLanguageCreate(BaseModel):
    language_id: int

class AvailableLanguage(BaseModel):
    language_id: int
    name: str
    iso_639_1: str