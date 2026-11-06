import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.provider import EventsProviderClient
from app.db_depends import get_async_db
from app.schemas.event import EventDetailOut, PaginatedEventOut
from app.services.events import EventService

router = APIRouter(prefix="/api/events",
                   tags=["Events"])


async def get_events_client():
    client = EventsProviderClient()
    try:
        yield client
    finally:
        await client.close()



async def get_event_service(
    db: AsyncSession = Depends(get_async_db),
    client: EventsProviderClient = Depends(get_events_client)) -> EventService:
    """создает логику работы (класс EventService) при каждом запросе в эндпоинт и передает ему текущую сессию БД и клиент"""
    return EventService(db, client)


@router.get("", response_model=PaginatedEventOut)
async def get_events(
    request: Request,
    date_from: date | None = Query(None, description="Дата для фильтрации"),

    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: EventService = Depends(get_event_service)
):
    """Получение всех событий"""
    return await service.list_events(page, page_size, date_from, request)



@router.get("/{event_id}", response_model=EventDetailOut)
async def get_event(event_id: uuid.UUID,
                    service: EventService = Depends(get_event_service)):
    """получить одно, конкретное событие"""
    return await service.get_event_details(event_id)



@router.get("/{event_id}/seats")
async def get_event_seats(event_id: uuid.UUID,
                          service: EventService = Depends(get_event_service)):
    """Получение списка свободных мест"""
    return await service.get_available_seats(event_id)
   
