from fastapi import APIRouter, Depends

from app.dependencies import get_sync_service
from app.services.sync import SyncService

router = APIRouter(prefix="/api", tags=["System"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/sync/trigger")
async def trigger_sync(
        service: SyncService = Depends(get_sync_service),
    ):
    await service.sync_events()
    return {"status": "success", "detail": "Синхронизация успешно выполнена"}
