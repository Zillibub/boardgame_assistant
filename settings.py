from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    discord_bot_token: str
    openai_token: str

    class Config:
        env_file = ".env"


settings = Settings()