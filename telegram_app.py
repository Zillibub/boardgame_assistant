from embedo.core.settings import settings
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)
from pathlib import Path
from datetime import datetime
from collections import deque, defaultdict
from embedo.chain.retrieval_chain_manager import RetrievalChainManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.chat_log import ChatLog

# Conversation history dictionary
conversation_history = defaultdict(lambda: deque(maxlen=10))

engine = create_engine(settings.USER_LOGS_DB, echo=True)

Session = sessionmaker(bind=engine)


def log_question_and_answer(chat_id, question, answer):
    session = Session()

    chat_log = ChatLog(chat_id=chat_id, question=question, answer=answer)
    session.add(chat_log)
    session.commit()

    session.close()


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    question = update.message.text

    chat_history = conversation_history[update.message.chat_id]

    result = await RetrievalChainManager(settings.vector_store_path).chain.acall(
        {"question": question, "chat_history": chat_history}
    )
    chat_history.append((question, result["answer"]))

    log_question_and_answer(update.message.chat_id, question, result["answer"])

    await update.message.reply_text(result["answer"])


async def ingest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("Please, attach a file to update the vector store")
        return
    if "zip" not in update.message.document.file_name:
        await update.message.reply_text("File must be a .zip archive")
        return
    file = await context.bot.get_file(update.message.document.file_id)
    file_path = Path(settings.VECTOR_STORE_FOLDER) / f"vector_store_{datetime.now()}/{update.message.document.file_name}"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    await file.download_to_drive(file_path)

    with open(Path(settings.VECTOR_STORE_FOLDER) / Path(settings.VECTOR_STORE_CURRENT_FILENAME), "w") as f:
        f.write(str(file_path))
    RetrievalChainManager.ingest(file_path)
    await update.message.reply_text("File downloaded successfully.")


def main():
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^Ingest"), answer))
    application.add_handler(MessageHandler(filters.Document.ALL, ingest))

    application.run_polling()


if __name__ == "__main__":
    main()