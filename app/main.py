import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import async_engine
from app.routers import events, system, tickets
from app.workers import run_sync_periodically

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Приложение запущено")
    sync_task = asyncio.create_task(run_sync_periodically())
    logger.info("Фоновая синхронизация запущена!")
    yield

    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        pass

    await async_engine.dispose()
    logger.info("Соединения с БД закрыты")



app = FastAPI(title="agregator", version="0.1.0", lifespan=lifespan)


app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(system.router)


@app.get("/")
async def welcome() -> dict:
    """Корневой маршрут"""
    return {"message": "Агрегатор"}