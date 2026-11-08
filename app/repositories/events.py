from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.enums import SyncStatus
from app.models import Event, Place, SyncMetadata


class SQLAlchemyEventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def commit(self) -> None:
        await self.db.commit()

    async def get_events_with_filters(
        self, page: int = 1, page_size: int = 20, date_from: date | None = None
    ) -> tuple[list[Event], int]:
        """Обычная пагинация"""

        query = select(Event).options(selectinload(Event.place))

        if date_from:
            filter_datetime = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=UTC)
            query = query.where(Event.event_time >= filter_datetime)

        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.db.scalar(count_query) or 0

        offset = (page - 1) * page_size
        query = query.order_by(Event.event_time).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all(), total_count

    async def get_event_by_id(self, event_id: UUID) -> Event | None:
        stmt = select(Event).where(Event.id == event_id).options(selectinload(Event.place))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


    async def get_sync_metadata(self):
        """Получить метаданные синхронизации (или создать, если их нет)"""
        stmt = select(SyncMetadata).where(SyncMetadata.id == 1)
        res = await self.db.scalars(stmt)
        meta = res.first()
        if not meta:
            meta = SyncMetadata(id=1, sync_status=SyncStatus.IDLE.value)
            self.db.add(meta)
            await self.db.commit()
        return meta

    async def update_sync_metadata(
        self, status: str, last_sync: datetime | None = None, last_changed: datetime | None = None
    ):
        """Обновить статус и время синхронизации"""
        meta = await self.get_sync_metadata()
        if last_sync:
            meta.last_sync_time = last_sync
        if last_changed:
            meta.last_changed_at = last_changed
        meta.sync_status = status
        await self.db.commit()


    async def upsert_batch(self, places: list[Place], events: list[Event]):
        """Вспомогательный метод для сохранения всей пачки данных ОДНИМ запросом (Bulk Upsert)."""
        if not places and not events:
            return

        if places:
            stmt = insert(Place)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "name": stmt.excluded.name,
                    "city": stmt.excluded.city,
                    "address": stmt.excluded.address,
                    "seats_pattern": stmt.excluded.seats_pattern,
                },
            )

            unique_places = {p.id: p for p in places}.values()

            places_dicts = [
                {
                    "id": p.id,
                    "name": p.name,
                    "city": p.city,
                    "address": p.address,
                    "seats_pattern": p.seats_pattern,
                }
                for p in unique_places
            ]

            await self.db.execute(stmt, places_dicts)

        if events:
            stmt = insert(Event)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "name": stmt.excluded.name,
                    "event_time": stmt.excluded.event_time,
                    "registration_deadline": stmt.excluded.registration_deadline,
                    "status": stmt.excluded.status,
                    "number_of_visitors": stmt.excluded.number_of_visitors,
                    "changed_at": stmt.excluded.changed_at,
                },
            )

            unique_events = {e.id: e for e in events}.values()

            events_dicts = [
                {
                    "id": e.id,
                    "place_id": e.place_id,
                    "name": e.name,
                    "event_time": e.event_time,
                    "registration_deadline": e.registration_deadline,
                    "status": e.status,
                    "number_of_visitors": e.number_of_visitors,
                    "changed_at": e.changed_at,
                }
                for e in unique_events
            ]

            await self.db.execute(stmt, events_dicts)
