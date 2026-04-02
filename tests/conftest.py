import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.main import app
from src.database import Base, get_async_session

# Создаем отдельную тестовую базу данных
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_app.db"

engine_test = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
async_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)


# Подменяем зависимость базы данных в FastAPI
async def override_get_async_session():
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


# Фикстура: создает таблицы перед тестами и удаляет после
@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Фикстура: асинхронный HTTP-клиент
@pytest.fixture(scope="session")
async def ac():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
