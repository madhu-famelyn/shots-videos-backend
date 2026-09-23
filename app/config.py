import os
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Echo Reels Bhojpuri API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "bhojpuri_secret_key_echo_reels_2026_super_secure")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_6PbepSi8IfxD@ep-lively-darkness-b372v1vf-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    )
    # MSG91 OTP Integration
    MSG91_AUTH_KEY: str = os.getenv("MSG91_AUTH_KEY", "572596A0fiy5sWd6aad138eP1")
    MSG91_TEMPLATE_ID: str = os.getenv("MSG91_TEMPLATE_ID", "")
    MSG91_OTP_LENGTH: int = int(os.getenv("MSG91_OTP_LENGTH", "4"))

    # Bunny Stream Integration
    BUNNY_STREAM_LIBRARY_ID: str = os.getenv("BUNNY_STREAM_LIBRARY_ID", "")
    BUNNY_STREAM_API_KEY: str = os.getenv("BUNNY_STREAM_API_KEY", "")
    BUNNY_STREAM_CDN_HOSTNAME: str = os.getenv("BUNNY_STREAM_CDN_HOSTNAME", "")
    BUNNY_STREAM_TOKEN_AUTH_KEY: str = os.getenv("BUNNY_STREAM_TOKEN_AUTH_KEY", "")

    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "*"
    ]

settings = Settings()

