from datetime import datetime, timezone, timedelta
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.core.config import settings
from app.core.database import async_session_factory, get_db
from app.db.redis import get_redis
from app.models.url import URL
from app.schemas.url import URLCreateRequest, URLCreateResponse, URLStatsResponse
from app.services.cache import get_cached_url, invalidate_cached_url, set_cached_url
from app.services.shortener import generate_short_code

router = APIRouter()


async def increment_clicks(short_code: str) -> None:
    async with async_session_factory() as db:
        await db.execute(
            update(URL)
            .where(URL.short_code == short_code)
            .values(click_count=URL.click_count + 1)
        )
        await db.commit()


@router.post("/shorten", response_model=URLCreateResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(
    request: URLCreateRequest,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> Any:
    # 1. Prevent shortening loops (cannot point back to own BASE_URL)
    long_url_str = str(request.long_url)
    base_url_normalized = settings.BASE_URL.rstrip("/") + "/"
    if long_url_str.startswith(base_url_normalized) or long_url_str == settings.BASE_URL.rstrip("/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot shorten a URL that points to this service itself"
        )

    # 2. Check if the same long_url was already shortened and hasn't expired
    stmt = select(URL).filter(
        URL.long_url == long_url_str
    ).filter(
        (URL.expires_at == None) | (URL.expires_at > datetime.now(timezone.utc))
    ).order_by(URL.created_at.desc())
    
    result = await db.execute(stmt)
    existing_url = result.scalar_one_or_none()
    if existing_url:
        return URLCreateResponse(
            short_code=existing_url.short_code,
            short_url=f"{settings.BASE_URL.rstrip('/')}/{existing_url.short_code}",
            long_url=existing_url.long_url,
            created_at=existing_url.created_at,
            expires_at=existing_url.expires_at,
        )

    # 3. Generate short code
    short_code = await generate_short_code(db)

    # 4. Compute expiration datetime if expires_in_days is set
    expires_at = None
    if request.expires_in_days is not None:
        if request.expires_in_days <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="expires_in_days must be a positive integer"
            )
        expires_at = datetime.now(timezone.utc) + timedelta(days=request.expires_in_days)

    # 5. Create URL row in Postgres
    db_url = URL(
        short_code=short_code,
        long_url=str(request.long_url),
        expires_at=expires_at,
    )
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)

    # 6. Cache in Redis
    ttl = settings.CACHE_TTL_SECONDS
    if expires_at:
        remaining = int((expires_at - datetime.now(timezone.utc)).total_seconds())
        if remaining > 0:
            ttl = min(ttl, remaining)
            await set_cached_url(redis_client, short_code, db_url.long_url, ttl)
    else:
        await set_cached_url(redis_client, short_code, db_url.long_url, ttl)

    # 7. Return response
    return URLCreateResponse(
        short_code=db_url.short_code,
        short_url=f"{settings.BASE_URL.rstrip('/')}/{db_url.short_code}",
        long_url=db_url.long_url,
        created_at=db_url.created_at,
        expires_at=db_url.expires_at,
    )


@router.get("/{short_code}")
async def redirect_url(
    short_code: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> RedirectResponse:
    # 1. Check Redis cache first
    cached_url = await get_cached_url(redis_client, short_code)
    if cached_url:
        background_tasks.add_task(increment_clicks, short_code)
        return RedirectResponse(url=cached_url, status_code=status.HTTP_302_FOUND)

    # 2. Cache miss, query Postgres
    result = await db.execute(select(URL).filter(URL.short_code == short_code))
    db_url = result.scalar_one_or_none()

    if not db_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )

    # 3. Check if expired
    if db_url.expires_at and db_url.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Short URL has expired"
        )

    # 4. Populate Redis cache
    ttl = settings.CACHE_TTL_SECONDS
    if db_url.expires_at:
        remaining = int((db_url.expires_at - datetime.now(timezone.utc)).total_seconds())
        if remaining > 0:
            ttl = min(ttl, remaining)
            await set_cached_url(redis_client, short_code, db_url.long_url, ttl)
    else:
        await set_cached_url(redis_client, short_code, db_url.long_url, ttl)

    # 5. Redirect and increment click count asynchronously
    background_tasks.add_task(increment_clicks, short_code)
    return RedirectResponse(url=db_url.long_url, status_code=status.HTTP_302_FOUND)


@router.get("/analytics/{short_code}", response_model=URLStatsResponse)
async def get_analytics(
    short_code: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    # Query Postgres directly (bypass cache — needs accurate click_count)
    result = await db.execute(select(URL).filter(URL.short_code == short_code))
    db_url = result.scalar_one_or_none()

    if not db_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )

    return db_url


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> None:
    # Query Postgres
    result = await db.execute(select(URL).filter(URL.short_code == short_code))
    db_url = result.scalar_one_or_none()

    if not db_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )

    # Delete row
    db.delete(db_url)
    await db.commit()

    # Invalidate Redis cache
    await invalidate_cached_url(redis_client, short_code)

