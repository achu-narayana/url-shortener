import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi import status
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import get_db
from app.db.redis import get_redis
from app.models.url import Base, URL

import pytest_asyncio

# Test SQLite Setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
_test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
_test_session_factory = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


# Mock Redis Setup
class MockRedis:
    def __init__(self):
        self.store = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.store[key] = value

    async def delete(self, key: str) -> None:
        self.store.pop(key, None)

    async def flushdb(self) -> None:
        self.store.clear()

    async def aclose(self) -> None:
        pass


mock_redis_client = MockRedis()


# Dependency Overrides
async def override_get_db():
    async with _test_session_factory() as session:
        yield session


async def override_get_redis():
    yield mock_redis_client


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_redis] = override_get_redis


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    # Create tables
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def mock_generate_short_code():
    counter = 0
    def side_effect(*args, **kwargs):
        nonlocal counter
        counter += 1
        return f"testcode{counter}"
    
    with patch("app.api.routes.generate_short_code", side_effect=side_effect) as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_session_factory():
    with patch("app.api.routes.async_session_factory", _test_session_factory):
        yield


@pytest_asyncio.fixture(autouse=True)
async def clear_redis():
    await mock_redis_client.flushdb()
    yield


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac


# Tests

@pytest.mark.asyncio
async def test_post_shorten_valid(client):
    payload = {"long_url": "https://example.com/valid", "expires_in_days": 10}
    response = await client.post("/shorten", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == "testcode1"
    assert "https://example.com/valid" in data["long_url"]
    assert "testcode1" in data["short_url"]


@pytest.mark.asyncio
async def test_post_shorten_twice_same_code(client):
    payload = {"long_url": "https://example.com/duplicate", "expires_in_days": 5}
    # First request
    response1 = await client.post("/shorten", json=payload)
    assert response1.status_code == 201
    data1 = response1.json()
    code1 = data1["short_code"]

    # Second request
    response2 = await client.post("/shorten", json=payload)
    assert response2.status_code == 201
    data2 = response2.json()
    code2 = data2["short_code"]

    assert code1 == code2
    assert code1 == "testcode1"


@pytest.mark.asyncio
async def test_get_redirect_valid(client):
    # Shorten first
    payload = {"long_url": "https://example.com/redirect-me"}
    create_res = await client.post("/shorten", json=payload)
    assert create_res.status_code == 201
    code = create_res.json()["short_code"]

    # Redirect GET
    redirect_res = await client.get(f"/{code}", follow_redirects=False)
    assert redirect_res.status_code == 302
    assert redirect_res.headers["location"] == "https://example.com/redirect-me"


@pytest.mark.asyncio
async def test_get_redirect_nonexistent(client):
    response = await client.get("/nonexistent-code")
    assert response.status_code == 404
    assert response.json()["detail"] == "Short URL not found"


@pytest.mark.asyncio
async def test_analytics_click_count(client):
    # Shorten first
    payload = {"long_url": "https://example.com/analytics-test"}
    create_res = await client.post("/shorten", json=payload)
    assert create_res.status_code == 201
    code = create_res.json()["short_code"]

    # Perform a few redirects
    num_redirects = 3
    for _ in range(num_redirects):
        res = await client.get(f"/{code}")
        assert res.status_code == 302

    # Give FastAPI's BackgroundTasks a brief moment to run and commit DB changes
    await asyncio.sleep(0.5)

    # Check analytics
    analytics_res = await client.get(f"/analytics/{code}")
    assert analytics_res.status_code == 200
    data = analytics_res.json()
    assert data["click_count"] == num_redirects
