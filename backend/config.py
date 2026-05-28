import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

root = Path(__file__).resolve().parent
load_dotenv(root / ".env")


def _build_postgres_uri() -> str:
    user = os.environ.get("DB_USER", "perfuser")
    password = os.environ.get("DB_PASSWORD", "perfpass")
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "perfdb")

    return (
        f"postgresql://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{name}"
    )


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

    # "sql" or "nosql"
    DB_TYPE = os.environ.get("DB_TYPE", "sql")

    # ---------- SQL (PostgreSQL) ----------
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or _build_postgres_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------- NoSQL (MongoDB) ----------
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "perfdb")
