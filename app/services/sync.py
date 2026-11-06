import logging
from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import insert

from app.clients.paginator import EventsPaginator
from app.clients.provider import EventsProviderClient
from app.models import Event, Place
from app.repositories.events import SQLAlchemyEventRepository

logger = logging.getLogger(__name__)

class SyncService:
    def __init__(self, repo: SQLAlchemyEventRepository, client: EventsProviderClient):
        self.repo = repo
        self.client = client


    def _parse_datetime(self, iso_string: str) -> datetime | None:
        """Берем дату и переводим её к общему часовому поясу UTC"""
        if not iso_string:
            return None
        return datetime.fromisoformat(iso_string).astimezone(UTC)


    async def sync_events(self):
        await self.repo.update_sync_metadata(status="in_progress")
        meta = await self.repo.get_sync_metadata()

        if meta and meta.last_changed_at:
            changed_at_param = meta.last_changed_at.strftime("%Y-%m-%d")
        else:
            changed_at_param = "2000-01-01"

        total_synced = 0
        max_changed_at = None

        batch_places = []
        batch_events = []

        try:
            paginator = EventsPaginator(self.client, changed_at=changed_at_param)
            
            async for item in paginator:
                total_synced += 1

                place_data = item["place"]
                new_place = Place(
                    id=place_data["id"],
                    name=place_data["name"],
                    city=place_data["city"],
                    address=place_data["address"],
                    seats_pattern=place_data["seats_pattern"]
                )
                batch_places.append(new_place)

                item_date = self._parse_datetime(item["changed_at"])
                if item_date and (max_changed_at is None or item_date > max_changed_at):
                    max_changed_at = item_date

                new_event = Event(
                    id=item["id"],
                    place_id=place_data["id"],
                    name=item["name"],
                    event_time=self._parse_datetime(item["event_time"]),
                    registration_deadline=self._parse_datetime(item["registration_deadline"]),
                    status=item["status"],
                    number_of_visitors=item["number_of_visitors"],
                    changed_at=self._parse_datetime(item["changed_at"])
                )
                batch_events.append(new_event)

                if len(batch_events) >= 20:
                    await self._save_batch(batch_places, batch_events)
                    batch_places.clear()
                    batch_events.clear()

            if batch_events:
                await self._save_batch(batch_places, batch_events)

            await self.repo.commit()
            await self.repo.update_sync_metadata(
                status="success",
                last_sync=datetime.now(UTC),
                last_changed=max_changed_at
            ) 
            logger.info("Синхронизация завершена. Обработано: %s", total_synced)


        except Exception as e:
            await self.repo.update_sync_metadata(status="failed")
            logger.error("Ошибка: %s", e, exc_info=True)
            raise 


    async def _save_batch(self, places: list[Place], events: list[Event]):
        """Вспомогательный метод для сохранения всей пачки данных ОДНИМ запросом (Bulk Upsert)."""
        if not places and not events:
            return

        if places:
            stmt = insert(Place)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={
                    'name': stmt.excluded.name,
                    'city': stmt.excluded.city,
                    'address': stmt.excluded.address,
                    'seats_pattern': stmt.excluded.seats_pattern
                }
            )

            unique_places = {p.id: p for p in places}.values()
            
            places_dicts = [
                {
                    "id": p.id,
                    "name": p.name,
                    "city": p.city,
                    "address": p.address,
                    "seats_pattern": p.seats_pattern
                }
                for p in unique_places
            ]
            
            await self.repo.db.execute(stmt, places_dicts)

        if events:
            stmt = insert(Event)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={
                    'name': stmt.excluded.name,
                    'event_time': stmt.excluded.event_time,
                    'registration_deadline': stmt.excluded.registration_deadline,
                    'status': stmt.excluded.status,
                    'number_of_visitors': stmt.excluded.number_of_visitors,
                    'changed_at': stmt.excluded.changed_at
                }
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
                    "changed_at": e.changed_at
                }
                for e in unique_events
            ]
            
            await self.repo.db.execute(stmt, events_dicts)











