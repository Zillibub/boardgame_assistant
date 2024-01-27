from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    discord_bot_token: str
    openai_token: str
    assistant_id: str
    telegram_bot_token: str
    USER_LOGS_DB: str = "sqlite:///database.db"

    class Config:
        env_file = ".env"


settings = Settings(_env_file=".env", _env_file_encoding='utf-8')
