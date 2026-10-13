
import os
import logging
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "inventory_db")

if not DB_USER or not DB_PASSWORD:
    raise RuntimeError(
        "Database configuration is incomplete. "
        "Set DB_USER and DB_PASSWORD in your .env file."
    )

DATABASE_URL = (
    f"mysql+pymysql://{quote_plus(DB_USER)}:"
    f"{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/"
    f"{DB_NAME}?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": 5},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection():
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
    except SQLAlchemyError as exc:
        logger.error(
            "Database connection failed (%s). Check MySQL service, "
            "host, port, database, username, password, and privileges.",
            type(exc).__name__,
        )
        raise RuntimeError(
            "Unable to connect to MySQL. Check the server and .env settings."
        ) from None
