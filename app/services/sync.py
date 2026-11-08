import logging
from datetime import UTC, datetime

from app.clients.paginator import EventsPaginator
from app.clients.provider import EventsProviderClient
from app.enums import SyncStatus
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
        """Синхронизация"""
        await self.repo.update_sync_metadata(status=SyncStatus.IN_PROGRESS.value)
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
                    seats_pattern=place_data["seats_pattern"],
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
                    changed_at=self._parse_datetime(item["changed_at"]),
                )
                batch_events.append(new_event)

                if len(batch_events) >= 20:
                    await self.repo.upsert_batch(batch_places, batch_events)
                    batch_places.clear()
                    batch_events.clear()

            if batch_events:
                await self.repo.upsert_batch(batch_places, batch_events)

            await self.repo.commit()
            await self.repo.update_sync_metadata(
                status=SyncStatus.SUCCESS.value,
                last_sync=datetime.now(UTC),
                last_changed=max_changed_at,
            )
            logger.info("Синхронизация завершена. Обработано: %s", total_synced)

        except Exception as e:
            await self.repo.db.rollback()
            await self.repo.update_sync_metadata(status=SyncStatus.FAILED.value)
            logger.error("Ошибка: %s", e, exc_info=True)
            raise


