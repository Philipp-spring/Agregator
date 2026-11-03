# Репозиторий - это модуль, который формирует запросы к нашей БД
from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Event, Place, SyncMetadata


class SQLAlchemyEventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db



    async def get_existing_events_by_ids(self, event_ids: set[str]) -> dict[str, Event]:
        """Поиск событий в БД, которые там уже есть"""
        if not event_ids:
            return {}
        stmt = select(Event).where(Event.id.in_(event_ids))
        result = await self.db.scalars(stmt)
        return {event.id: event for event in result.all()}


    async def get_existing_places_by_ids(self, place_ids: set[str]) -> dict[str, Place]:
        if not place_ids:
            return {}
        stmt = select(Place).where(Place.id.in_(place_ids))
        result = await self.db.scalars(stmt)
        return {place.id: place for place in result.all()}


    async def create_event(self, event: Event) -> None:
        self.db.add(event)


    async def create_events(self, events: list[Event]) -> None:
        if events: self.db.add_all(events)


    async def create_place(self, place: Place) -> None:
        self.db.add(place)


    async def create_places(self, places: list[Place]) -> None:
        if places: self.db.add_all(places)


    async def merge_event(self, event: Event) -> Event:
        return await self.db.merge(event)


    async def flush(self) -> None:
        await self.db.flush()


    async def commit(self) -> None:
        await self.db.commit()


    async def get_events_with_filters(self, page: int = 1,
                                      page_size: int = 20,
                                      date_from: date | None = None) -> tuple[list[Event], int]:
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
            meta = SyncMetadata(id=1, sync_status="idle")
            self.db.add(meta)
            await self.db.commit()
        return meta



    async def update_sync_metadata(self,
        status: str,
        last_sync: datetime | None = None,
        last_changed: datetime | None = None
    ):
        """Обновить статус и время синхронизации"""
        meta = await self.get_sync_metadata()
        if last_sync:
            meta.last_sync_time = last_sync
        if last_changed:
            meta.last_changed_at = last_changed
        meta.sync_status = status
        await self.db.commit()
