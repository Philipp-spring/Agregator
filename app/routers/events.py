import uuid
from datetime import date
from urllib.parse import urlencode, urljoin

from fastapi import APIRouter, Depends, Query, Request

from app.dependencies import get_event_service
from app.schemas.event import EventDetailOut, EventSeatsOut, PaginatedEventOut
from app.services.events import EventService

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("", response_model=PaginatedEventOut)
async def get_events(
    request: Request,
    date_from: date | None = Query(None, description="Дата для фильтрации"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: EventService = Depends(get_event_service),
):
    """Получение всех событий"""
    data = await service.list_events(page, page_size, date_from)

    base_url = str(request.base_url).rstrip("/")
    next_url = None
    previous_url = None

    if (page * page_size) < data["count"]:
        params = {"page": page + 1, "page_size": page_size}
        if date_from:
            params["date_from"] = str(date_from)
        next_url = urljoin(base_url, f"/api/events/?{urlencode(params)}")

    if page > 1:
        params = {"page": page - 1, "page_size": page_size}
        if date_from:
            params["date_from"] = str(date_from)
        previous_url = urljoin(base_url, f"/api/events/?{urlencode(params)}")

    return {
        "count": data["count"],
        "next": next_url,
        "previous": previous_url,
        "results": data["results"],
    }


@router.get("/{event_id}", response_model=EventDetailOut)
async def get_event(event_id: uuid.UUID, service: EventService = Depends(get_event_service)):
    """получить одно, конкретное событие"""
    return await service.get_event_details(event_id)


@router.get("/{event_id}/seats", response_model=EventSeatsOut)
async def get_event_seats(event_id: uuid.UUID, service: EventService = Depends(get_event_service)):
    """Получение списка свободных мест"""
    return await service.get_available_seats(event_id)
