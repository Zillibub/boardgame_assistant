from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings
from db.chat_log import ChatLog

engine = create_engine(settings.USER_LOGS_DB, echo=True)

Session = sessionmaker(bind=engine)
ChatLog.metadata.create_all(bind=engine)