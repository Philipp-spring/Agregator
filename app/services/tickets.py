import logging
import uuid
from datetime import UTC, datetime

import httpx

from app.clients.provider import EventsProviderClient
from app.exceptions import (
    EventNotFoundError,
    EventNotPublishedError,
    ProviderError,
    RegistrationDeadlinePassedError,
    SeatNotAvailableError,
    TicketIdMissingError,
)
from app.repositories.tickets import SQLAlchemyTicketRepository

logger = logging.getLogger(__name__)

class TicketService:
    """Бизнес-сценарий создания билета с интеграцией провайдера."""

    def __init__(self, client: EventsProviderClient, repo: SQLAlchemyTicketRepository):
        self.client = client
        self.repo = repo

    async def create_ticket(self, event_id: uuid.UUID, first_name: str, last_name: str, email: str, seat: str) -> str:
        event = await self.repo.get_event(event_id)
        if not event:
            logger.warning("Попытка регистрации на несуществующее событие %s", event_id)
            raise EventNotFoundError("Событие не найдено")

        if event.status != "published":
            raise EventNotPublishedError("Регистрация доступна только для опубликованных событий")


        now = datetime.now(UTC)
        deadline = event.registration_deadline.astimezone(UTC)
        if now >= deadline:
            raise RegistrationDeadlinePassedError("Срок регистрации на это мероприятие истек")
        try:
            seats_data = await self.client.get_seats(event_id)
        except httpx.HTTPError as e:
            raise ProviderError(f"Не удалось проверить места: {e}")

        if seat not in seats_data.get("seats", []):
            raise SeatNotAvailableError(f"Место {seat} занято или не существует")

        try:
            response_data = await self.client.register(
                event_id=event_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                seat=seat
            )
        except httpx.HTTPError as e:
            raise ProviderError(f"Ошибка регистрации: {e}")

        ticket_id = response_data.get("ticket_id")
        if not ticket_id:
            raise TicketIdMissingError("Внешний API не вернул ticket_id")

        await self.repo.create(
            event_id=event_id,
            ticket_id=uuid.UUID(ticket_id),
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat
        )

        await self.repo.db.commit()

        logger.info("Успешная регистрация билета %s у провайдера и в локальной БД", ticket_id)
        return ticket_id
