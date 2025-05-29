import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    
    async def get_test_db():
        async with async_session_maker() as session:
            yield session
    
    app.dependency_overrides[get_db] = get_test_db
    
    yield async_session_maker
    
    app.dependency_overrides.clear()

@pytest.fixture
async def client(test_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
