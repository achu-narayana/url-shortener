from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="URL Shortener", lifespan=lifespan)
app.include_router(router)
