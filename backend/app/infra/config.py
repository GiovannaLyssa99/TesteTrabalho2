from dotenv import load_dotenv
import os

load_dotenv()  # ou só load_dotenv() se estiver na root

class Config:

    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/chatbotinova"
    )
    DB_URI = os.getenv("DB_URI")

    # REDIS_HOST = os.getenv("REDIS_HOST")
    # REDIS_PORT = os.getenv("REDIS_PORT")
    # REDIS_DB = os.getenv("REDIS_DB")
    # REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")