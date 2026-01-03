from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import config
from backend.utils.logger import logger
engine = create_engine(
    config.database.url,
    echo=config.server.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def init_db():
    logger.info("Initializing database...")
    try:
        from backend.models.event import Event
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
def drop_db():
    logger.warning("Dropping all database tables!")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    logger.debug("New database connection established")
@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    logger.debug("Database connection closed")
