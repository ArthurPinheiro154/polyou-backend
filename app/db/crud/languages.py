from sqlalchemy.orm import Session
from sqlalchemy import select

from ...schemas.languages import AvailableLanguage
from ...db.models import Languages

def get_available_languages(db: Session) -> list[AvailableLanguage]:
    stmt = select(Languages)
    query_languages = db.execute(stmt).scalars().all()
    
    languages = [
        AvailableLanguage(language_id= query_language.language_id,
                           name= query_language.name, 
                           iso_639_1= query_language.iso_639_1) 
                           for query_language in query_languages
    ]

    return languages

    
