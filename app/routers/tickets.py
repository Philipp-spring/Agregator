import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.provider import EventsProviderClient
from app.db_depends import get_async_db
from app.repositories.tickets import SQLAlchemyTicketRepository
from app.schemas.ticket import TicketCreate, TicketOut
from app.services.tickets import TicketService

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


async def get_events_client():
    client = EventsProviderClient()
    try:
        yield client
    finally:
        await client.close()


async def get_create_ticket(
    db: AsyncSession = Depends(get_async_db),
    client: EventsProviderClient = Depends(get_events_client)):
    repo = SQLAlchemyTicketRepository(db)
    return TicketService(client=client, repo=repo)



@router.post("", response_model=TicketOut, status_code=201)
async def create_ticket(
        ticket_data: TicketCreate,
        service: TicketService = Depends(get_create_ticket)):


    ticket_id = await service.create_ticket(
        event_id=ticket_data.event_id,
        first_name=ticket_data.first_name,
        last_name=ticket_data.last_name,
        email=ticket_data.email,
        seat=ticket_data.seat,
    )
    return {"ticket_id": ticket_id}




@router.delete("/{ticket_id}")
async def cancel_ticket(
        ticket_id: uuid.UUID, 
        service: TicketService = Depends(get_create_ticket)):
    """Отмена регистрации (билета)"""
    await service.cancel_ticket(ticket_id)
    return {"success": True}



