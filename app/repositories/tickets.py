import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, Ticket


class SQLAlchemyTicketRepository:
    """Репозитарий для работы с билетами в БД"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_event(self, event_id: uuid.UUID) -> Event | None:
        """Получить событие из локальной БД для валидации"""
        stmt = select(Event).where(Event.id == event_id)
        event = await self.db.scalars(stmt)
        return event.first()


    async def get_ticket_by_id(self, ticket_id: uuid.UUID) -> Ticket | None:
        """Получить билет из БД по его ID"""
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        res = await self.db.scalars(stmt)
        return res.first()
    


    async def create(self, event_id: uuid.UUID, ticket_id: uuid.UUID, first_name: str, last_name: str, email: str, seat: str) -> None:
        """Создание и сохранение объекта билета в локальную БД после ответа от внешнего API."""
        new_ticket = Ticket(
            id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,

        )
        self.db.add(new_ticket)
        await self.db.flush()



    async def delete(self, ticket_id: uuid.UUID) -> None:
        """Жесткое удаление билета при отмене"""
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        ticket = (await self.db.execute(stmt)).scalar_one_or_none()
        if ticket:
            await self.db.delete(ticket)
            await self.db.flush()
