from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from ..core.config import settings

engine = create_engine("postgresql://postgres:password@localhost:5432/polyou", echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=True,
    future=True
)