import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

    # "sql" or "nosql"
    DB_TYPE = os.environ.get("DB_TYPE", "sql")

    # ---------- SQL (PostgreSQL) ----------
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://perfuser:perfpass@localhost:5432/perfdb",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------- NoSQL (MongoDB) ----------
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "perfdb")
