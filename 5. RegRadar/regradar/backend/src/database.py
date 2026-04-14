"""
Database Module

Handles SQLAlchemy engine initialization, session management,
connection pooling, and database operations.
"""

import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from src.config import settings
from src.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connection and session lifecycle."""

    _engine: Optional[Engine] = None
    _session_maker: Optional[sessionmaker] = None

    @classmethod
    def initialize(cls, database_url: Optional[str] = None) -> None:
        """
        Initialize database engine and session maker.

        Args:
            database_url: Database URL. Defaults to settings.database_url
        """
        if database_url is None:
            database_url = settings.database_url

        logger.info(f"Initializing database: {database_url}")

        try:
            if "sqlite" in database_url:
                # SQLite for development/testing
                cls._engine = create_engine(
                    database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=settings.debug,
                )
            else:
                # PostgreSQL for production
                cls._engine = create_engine(
                    database_url,
                    pool_size=5,
                    max_overflow=10,
                    echo=settings.debug,
                )

            cls._session_maker = sessionmaker(
                bind=cls._engine,
                expire_on_commit=False,
                autoflush=False,
            )

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    @classmethod
    def get_session(cls) -> Session:
        """
        Get a database session.

        Returns:
            SQLAlchemy Session

        Raises:
            RuntimeError: If database not initialized
        """
        if cls._session_maker is None:
            raise RuntimeError("Database not initialized. Call DatabaseManager.initialize() first.")
        return cls._session_maker()

    @classmethod
    def get_engine(cls) -> Engine:
        """
        Get the database engine.

        Returns:
            SQLAlchemy Engine

        Raises:
            RuntimeError: If database not initialized
        """
        if cls._engine is None:
            raise RuntimeError("Database not initialized. Call DatabaseManager.initialize() first.")
        return cls._engine

    @classmethod
    def create_all_tables(cls) -> None:
        """Create all tables defined in models.Base."""
        if cls._engine is None:
            raise RuntimeError("Database not initialized")

        logger.info("Creating database tables...")
        try:
            Base.metadata.create_all(cls._engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise

    @classmethod
    def drop_all_tables(cls) -> None:
        """
        Drop all tables. WARNING: Destructive operation.

        This should only be used in development/testing.
        """
        if cls._engine is None:
            raise RuntimeError("Database not initialized")

        if not settings.is_development():
            raise RuntimeError("Cannot drop tables in production")

        logger.warning("Dropping all database tables...")
        try:
            Base.metadata.drop_all(cls._engine)
            logger.info("All tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop tables: {str(e)}")
            raise

    @classmethod
    def check_connection(cls) -> bool:
        """
        Check if database is accessible.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            if cls._engine is None:
                return False

            with cls._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.warning(f"Database connection check failed: {str(e)}")
            return False

    @classmethod
    def get_table_count(cls) -> int:
        """
        Get number of tables in the database.

        Returns:
            Number of tables
        """
        if cls._engine is None:
            return 0

        try:
            inspector = inspect(cls._engine)
            tables = inspector.get_table_names()
            return len(tables)
        except Exception as e:
            logger.warning(f"Failed to count tables: {str(e)}")
            return 0


# Dependency injection for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get database session.

    Yields:
        SQLAlchemy Session
    """
    session = DatabaseManager.get_session()
    try:
        yield session
    finally:
        session.close()


async def init_db() -> None:
    """Initialize database on application startup."""
    logger.info("Database initialization starting...")

    try:
        # Initialize database manager
        DatabaseManager.initialize()

        # Create all tables
        DatabaseManager.create_all_tables()

        # Verify connection
        if DatabaseManager.check_connection():
            logger.info("Database is ready")
        else:
            logger.error("Database connection verification failed")
            raise RuntimeError("Database connection verification failed")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


async def close_db() -> None:
    """Close database connection on application shutdown."""
    logger.info("Closing database connection...")
    try:
        engine = DatabaseManager.get_engine()
        engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Failed to close database: {str(e)}")
