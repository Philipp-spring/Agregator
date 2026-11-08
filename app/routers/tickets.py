import uuid

from fastapi import APIRouter, Depends

from app.dependencies import get_create_ticket
from app.schemas.ticket import TicketCreate, TicketOut
from app.services.tickets import TicketService

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("", response_model=TicketOut, status_code=201)
async def create_ticket(
    ticket_data: TicketCreate, service: TicketService = Depends(get_create_ticket)
):

    ticket_id = await service.create_ticket(
        event_id=ticket_data.event_id,
        first_name=ticket_data.first_name,
        last_name=ticket_data.last_name,
        email=ticket_data.email,
        seat=ticket_data.seat,
    )
    return {"ticket_id": ticket_id}


@router.delete("/{ticket_id}")
async def cancel_ticket(ticket_id: uuid.UUID, service: TicketService = Depends(get_create_ticket)):
    """Отмена регистрации (билета)"""
    await service.cancel_ticket(ticket_id)
    return {"success": True}
