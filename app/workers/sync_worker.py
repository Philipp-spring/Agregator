import asyncio
import logging

from app.clients.provider import EventsProviderClient
from app.database import async_session_maker
from app.repositories.events import SQLAlchemyEventRepository
from app.services.sync import SyncService

logger = logging.getLogger(__name__)


async def run_sync_periodically():
    """Бесконечный цикл, который дергает синхронизацию каждые N минут"""
    while True:
        try:
            logger.info("Запуск фоновой синхронизации...")
            async with async_session_maker() as db:
                async with EventsProviderClient() as client:
                    repo = SQLAlchemyEventRepository(db)
                    service = SyncService(repo=repo, client=client)
                    await service.sync_events()
                    logger.info("Синхронизация завершена")
        except Exception as e:
            logger.error("Ошибка в воркере: %s" , e, exc_info=True)


        await asyncio.sleep(86400)
