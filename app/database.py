from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)