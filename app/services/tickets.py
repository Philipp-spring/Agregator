import logging
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException

from app.clients.provider import EventsProviderClient
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
            logger.warning(f"Попытка регистрации на несуществующее событие {event_id}")
            raise HTTPException(status_code=404, detail="Событие не найдено")

        if event.status != "published":
            raise HTTPException(status_code=400, detail="Регистрация доступна только для опубликованных событий")


        now = datetime.now(UTC)
        deadline = event.registration_deadline.astimezone(UTC)
        if now >= deadline:
            raise HTTPException(status_code=400, detail="Срок регистрации на это мероприятие истек")
        try:
            seats_data = await self.client.get_seats(event_id)
            if seat not in seats_data.get("seats", []):
                raise HTTPException(status_code=400, detail=f"Место {seat} занято или не существует")
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Не удалось проверить места: {e}")

        try:
            response_data = await self.client.register(
                event_id=event_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                seat=seat
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка регистрации: {str(e)}")

        ticket_id = response_data.get("ticket_id")
        if not ticket_id:
            raise HTTPException(status_code=500, detail="Внешний API не вернул ticket_id")

        await self.repo.create(
            event_id=event_id,
            ticket_id=uuid.UUID(ticket_id),
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat
        )

        await self.repo.db.commit()

        logger.info(f"Успешная регистрация билета {ticket_id} у провайдера и в локальной БД")
        return ticket_id
