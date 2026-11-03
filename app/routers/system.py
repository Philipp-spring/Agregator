from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.provider import EventsProviderClient
from app.db_depends import get_async_db
from app.repositories.events import SQLAlchemyEventRepository
from app.services.sync import SyncService

router = APIRouter(prefix="/api", tags=["System"])



async def get_events_client():
    client = EventsProviderClient()
    try:
        yield client
    finally:
        await client.close()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/sync/trigger")
async def trigger_sync(
        db: AsyncSession = Depends(get_async_db),
        client: EventsProviderClient = Depends(get_events_client)):

    repo = SQLAlchemyEventRepository(db)
    service = SyncService(repo=repo, client=client)

    await service.sync_events()

    return {
        "status": "success",
        "detail": "Синхронизация успешно выполнена"
    }
