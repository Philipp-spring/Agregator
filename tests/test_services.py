import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from app.clients.provider import EventsProviderClient
from app.models import Event
from app.repositories.events import SQLAlchemyEventRepository
from app.services.events import EventService


@pytest.mark.asyncio
async def test_get_event_details_success():
    """Тест: сервис возвращает событие, если оно есть в БД."""
    mock_db = AsyncMock()
    mock_client = AsyncMock(spec=EventsProviderClient)
    

    event_id = uuid.uuid4()
    mock_event = Event(
        id=event_id, name="Тест", status="published", 
        registration_deadline=datetime.now(UTC) + timedelta(days=1),
        event_time=datetime.now(UTC) + timedelta(days=2),
        place_id=uuid.uuid4(), number_of_visitors=0, changed_at=datetime.now(UTC)
    )

    service = EventService(db=mock_db, client=mock_client)
    service.repo = AsyncMock(spec=SQLAlchemyEventRepository)
    service.repo.get_event_by_id.return_value = mock_event

    result = await service.get_event_details(event_id)

    assert result == mock_event
    service.repo.get_event_by_id.assert_called_once_with(event_id)


@pytest.mark.asyncio
async def test_get_available_seats_caching():
    """Тест: кэширование мест работает (второй запрос не идет в API)."""
    mock_db = AsyncMock()
    mock_client = AsyncMock(spec=EventsProviderClient)
    
    event_id = uuid.uuid4()
    mock_event = Event(
        id=event_id, name="Тест", status="published", 
        registration_deadline=datetime.now(UTC) + timedelta(days=1),
        event_time=datetime.now(UTC) + timedelta(days=2),
        place_id=uuid.uuid4(), number_of_visitors=0, changed_at=datetime.now(UTC)
    )
    
    service = EventService(db=mock_db, client=mock_client)
    service.repo = AsyncMock(spec=SQLAlchemyEventRepository)
    service.repo.get_event_by_id.return_value = mock_event

    mock_client.get_seats.return_value = {"seats": ["A1", "A2"]}

    result1 = await service.get_available_seats(event_id)
    assert result1["available_seats"] == ["A1", "A2"]
    assert mock_client.get_seats.call_count == 1

    result2 = await service.get_available_seats(event_id)
    assert result2["available_seats"] == ["A1", "A2"]
    assert mock_client.get_seats.call_count == 1
