import logging
import time
import uuid

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.provider import EventsProviderClient
from app.repositories.events import SQLAlchemyEventRepository

logger = logging.getLogger(__name__)



class EventService:
    def __init__(self, db: AsyncSession, client: EventsProviderClient):
        self.repo = SQLAlchemyEventRepository(db)
        self.client = client

        self._seats_cache = {}

    async def list_events(self, page, page_size, date_from=None, request: Request = None):
        """функция для эндпоинта, который показывает список всех событий в БД"""
        events, total = await self.repo.get_events_with_filters(page=page, page_size=page_size, date_from=date_from)

        next_url = None
        previous_url = None

        if request:
            base_url = str(request.base_url).rstrip("/")
            

            if (page * page_size) < total:
                next_url = f"{base_url}/api/events/?page={page + 1}&page_size={page_size}"
                if date_from:
                    next_url += f"&date_from={date_from}"

            if page > 1:
                previous_url = f"{base_url}/api/events/?page={page - 1}&page_size={page_size}"
                if date_from:
                    previous_url += f"&date_from={date_from}"
        
        return {"count": total,
                "next": next_url,
                "previous": previous_url,
                "results": events}



    async def get_event_details(self, event_id: uuid.UUID):
        """функция для эндпоинта, который показывает одно конкретное событие в БД"""
        event = await self.repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Событие не найдено")
        return event


    async def get_available_seats(self, event_id: uuid.UUID):
        """показ список свободных мест  (связывает БД и Внешний API)"""
        event = await self.repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Событие не найдено")
        if event.status != "published":
            raise HTTPException(status_code=400, detail="Событие не опубликовано")


        current_time = time.time()

        if event_id in self._seats_cache:
            cached_data, cached_time = self._seats_cache[event_id]
            if current_time - cached_time < 30:
                logger.info(f"Отдаем данные из кэша (ОЗУ) {event_id}")
                return cached_data


        try:
            seats_data = await self.client.get_seats(event_id)
            result = {"event_id": event_id, "available_seats": seats_data.get("seats", [])}
            self._seats_cache[event_id] = (result, current_time)

            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

