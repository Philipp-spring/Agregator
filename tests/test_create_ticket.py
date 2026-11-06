import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from app.clients.provider import EventsProviderClient
from app.exceptions import EventNotFoundError
from app.models import Event
from app.repositories.tickets import SQLAlchemyTicketRepository
from app.services.tickets import TicketService


@pytest.mark.asyncio
async def test_create_ticket_success():
    """Тест: успешное создание билета."""
    mock_repo = AsyncMock(spec=SQLAlchemyTicketRepository)
    mock_client = AsyncMock(spec=EventsProviderClient)
    
    # Добавляем мок для db
    mock_repo.db = AsyncMock()

    event_id = uuid.uuid4()
    mock_event = Event(
        id=event_id,
        name="Тестовое событие",
        status="published",
        registration_deadline=datetime.now(UTC) + timedelta(days=1),
        event_time=datetime.now(UTC) + timedelta(days=2),
        place_id=uuid.uuid4(),
        number_of_visitors=0,
        changed_at=datetime.now(UTC)
    )
    mock_repo.get_event.return_value = mock_event
    
    mock_client.get_seats.return_value = {"seats": ["A1", "A2", "A3"]}
    mock_client.register.return_value = {"ticket_id": str(uuid.uuid4())}
    
    service = TicketService(client=mock_client, repo=mock_repo)
    
    ticket_id = await service.create_ticket(
        event_id=event_id,
        first_name="Александр",
        last_name="Александров",
        email="alex@example.com",
        seat="A1"
    )
    
    assert ticket_id is not None
    mock_client.get_seats.assert_called_once_with(event_id)
    mock_client.register.assert_called_once()
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_ticket_event_not_found():
    """Тест: если события нет в БД, выбрасывается 404."""
    mock_repo = AsyncMock(spec=SQLAlchemyTicketRepository)
    mock_client = AsyncMock(spec=EventsProviderClient)
    mock_repo.db = AsyncMock() 
    
    mock_repo.get_event.return_value = None
    
    service = TicketService(client=mock_client, repo=mock_repo)
    
    with pytest.raises(EventNotFoundError) as exc_info:
        await service.create_ticket(
            event_id=uuid.uuid4(),
            first_name="Александр",
            last_name="Александров",
            email="alex@example.com",
            seat="A1"
        )
    
    assert str(exc_info.value) == "Событие не найдено"
