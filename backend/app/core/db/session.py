from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import APP_SETTINGS

engine = create_async_engine(APP_SETTINGS.DATABASE_URL)

session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
