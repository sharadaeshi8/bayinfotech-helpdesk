from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

print("--==-=---=-=--=-=-=-", settings.DATABASE_URL)

# For Supabase pooler, we need to completely disable connection pooling
# and prepared statements
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,  # Disable SQLAlchemy pooling, let Supabase handle it
    connect_args={
        "server_settings": {
            "jit": "off",
            "application_name": "bayinfotech-helpdesk",
        },
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize the database - create tables and enable pgvector extension."""
    try:
        from sqlalchemy import text
        
        # Use separate connections to avoid prepared statement conflicts
        async with engine.connect() as conn:
            async with conn.begin():
                # Enable pgvector extension
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("pgvector extension enabled")
        
        # Import models to register them with Base
        from app.models import models  # noqa: F401
        
        # Create tables in a separate connection
        async with engine.connect() as conn:
            async with conn.begin():
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")
