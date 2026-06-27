from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl


class URLCreateRequest(BaseModel):
    long_url: HttpUrl
    expires_in_days: int | None = None


class URLCreateResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: HttpUrl
    created_at: datetime
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class URLStatsResponse(BaseModel):
    short_code: str
    long_url: HttpUrl
    click_count: int
    created_at: datetime
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
