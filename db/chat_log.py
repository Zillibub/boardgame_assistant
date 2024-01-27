from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from core.settings import settings
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(settings.USER_LOGS_DB, echo=True)

Session = sessionmaker(bind=engine)

Base = declarative_base()


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)