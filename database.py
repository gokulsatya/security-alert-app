from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The database URL. For SQLite this is just a file path.
# "alerts.db" will be created automatically in the project folder.
SQLALCHEMY_DATABASE_URL = "sqlite:///./alerts.db"

# The "engine" is the core object that manages the connection to the DB file.
# check_same_thread=False is a SQLite-specific setting required because
# FastAPI may touch the database from more than one thread.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# A "session" is a temporary workspace for a batch of DB operations.
# SessionLocal is a factory: every time we call SessionLocal() we get a
# fresh session to read/write with, then close when done.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class our table model (in models.py) will inherit from.
# SQLAlchemy uses it to keep track of all our tables.
Base = declarative_base()