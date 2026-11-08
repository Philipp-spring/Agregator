import logging
import uuid

import httpx

from app.cache import get_cached_seats, set_cached_seats
from app.clients.provider import EventsProviderClient
from app.enums import EventStatus
from app.exceptions import EventNotFoundError, EventNotPublishedError, ProviderError
from app.repositories.events import SQLAlchemyEventRepository

logger = logging.getLogger(__name__)


class EventService:
    def __init__(self, repo: SQLAlchemyEventRepository, client: EventsProviderClient):
        self.repo = repo
        self.client = client

    async def list_events(self, page, page_size, date_from=None):
        """функция для эндпоинта, который показывает список всех событий в БД"""
        events, total = await self.repo.get_events_with_filters(
            page=page, page_size=page_size, date_from=date_from
        )
        return {"count": total, "results": events}

    async def get_event_details(self, event_id: uuid.UUID):
        """функция для эндпоинта, который показывает одно конкретное событие в БД"""
        event = await self.repo.get_event_by_id(event_id)
        if not event:
            raise EventNotFoundError("Событие не найдено")
        return event

    async def get_available_seats(self, event_id: uuid.UUID):
        """показ список свободных мест (связывает(использует) БД и Внешний API)"""
        event = await self.repo.get_event_by_id(event_id)
        if not event:
            raise EventNotFoundError("Событие не найдено")
        if event.status != EventStatus.PUBLISHED.value:
            raise EventNotPublishedError("Событие не опубликовано")

        cached_data = get_cached_seats(event_id)
        if cached_data is not None:
            logger.info("Отдаем данные из кэша (ОЗУ) %s", event_id)
            return cached_data

        try:
            seats_data = await self.client.get_seats(event_id)
            result = {"event_id": event_id, "available_seats": seats_data.get("seats", [])}
            set_cached_seats(event_id, result)
            return result
        except httpx.HTTPError as e:
            raise ProviderError(f"Не удалось получить места: {e}")
