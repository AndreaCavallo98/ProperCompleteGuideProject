from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@database/test_db"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with async_session_maker() as session:
        yield session
