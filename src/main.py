# import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.views import router
from core.config import settings
from db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[f'{settings.elastic_host}:{settings.elastic_port}'],
    )
    yield
    await redis.redis.close()
    await elastic.es.close()

app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(router, prefix='/api/v1')