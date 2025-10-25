from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8000
    mongodb_uri: str
    db_name: str = "book_reco"
    google_books_api_key: str = ""
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
