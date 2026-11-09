from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.provider import EventsProviderClient
from app.db_depends import get_async_db
from app.repositories.events import SQLAlchemyEventRepository
from app.repositories.tickets import SQLAlchemyTicketRepository
from app.services.events import EventService
from app.services.sync import SyncService
from app.services.tickets import TicketService


async def get_events_client(request: Request):
    return EventsProviderClient(request.app.state.http_client)


async def get_event_service(
    db: AsyncSession = Depends(get_async_db),
    client: EventsProviderClient = Depends(get_events_client),
) -> EventService:
    """создает логику работы (класс EventService) при каждом запросе в эндпоинт и передает ему текущую сессию БД и клиент"""
    repo = SQLAlchemyEventRepository(db)
    return EventService(repo=repo, client=client)


async def get_create_ticket(
    db: AsyncSession = Depends(get_async_db),
    client: EventsProviderClient = Depends(get_events_client),
) -> TicketService:
    repo = SQLAlchemyTicketRepository(db)
    return TicketService(client=client, repo=repo)


async def get_sync_service(
    db: AsyncSession = Depends(get_async_db),
    client: EventsProviderClient = Depends(get_events_client),
) -> SyncService:
    repo = SQLAlchemyEventRepository(db)
    return SyncService(repo=repo, client=client)
