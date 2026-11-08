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
    mock_client = AsyncMock(spec=EventsProviderClient)
    
    event_id = uuid.uuid4()
    mock_event = Event(
        id=event_id, name="Тест", status="published", 
        registration_deadline=datetime.now(UTC) + timedelta(days=1),
        event_time=datetime.now(UTC) + timedelta(days=2),
        place_id=uuid.uuid4(), number_of_visitors=0, changed_at=datetime.now(UTC)
    )
    
    mock_repo = AsyncMock(spec=SQLAlchemyEventRepository)
    mock_repo.get_event_by_id.return_value = mock_event

    service = EventService(repo=mock_repo, client=mock_client)

    result = await service.get_event_details(event_id)

    assert result == mock_event
    service.repo.get_event_by_id.assert_called_once_with(event_id)


@pytest.mark.asyncio
async def test_get_available_seats_caching():
    """Тест: кэш переживает создание нового инстанса сервиса (не пер-реквестный)."""
    mock_client = AsyncMock(spec=EventsProviderClient)

    event_id = uuid.uuid4()
    mock_event = Event(
        id=event_id, name="Тест", status="published",
        registration_deadline=datetime.now(UTC) + timedelta(days=1),
        event_time=datetime.now(UTC) + timedelta(days=2),
        place_id=uuid.uuid4(), number_of_visitors=0, changed_at=datetime.now(UTC),
    )
    mock_client.get_seats.return_value = {"seats": ["A1", "A2"]}
    
    mock_repo = AsyncMock(spec=SQLAlchemyEventRepository)
    mock_repo.get_event_by_id.return_value = mock_event

    service1 = EventService(repo=mock_repo, client=mock_client)

    result1 = await service1.get_available_seats(event_id)
    assert result1["available_seats"] == ["A1", "A2"]
    assert mock_client.get_seats.call_count == 1

    service2 = EventService(repo=mock_repo, client=mock_client)
 
    result2 = await service2.get_available_seats(event_id)
    assert result2["available_seats"] == ["A1", "A2"]
    assert mock_client.get_seats.call_count == 1   
