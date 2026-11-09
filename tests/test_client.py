import uuid
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from app.clients.provider import EventsProviderClient
from app.config import settings


@pytest.fixture
def events_url():
    """Возвращает URL для запроса событий (универсально для любого окружения)."""
    return f"{settings.api_base_url}/api/events/?changed_at=2000-01-01"


@pytest.mark.asyncio
async def test_get_events_success(httpx_mock, events_url):
    """Тест: клиент успешно делает запрос и возвращает JSON."""
    
    httpx_mock.add_response(
        url=events_url,
        method="GET",
        json={"results": [{"id": "1", "name": "Тест"}], "next": None},
        status_code=200
    )

    client = EventsProviderClient(httpx.AsyncClient(base_url=settings.api_base_url))
    try:
        result = await client.get_events(changed_at="2000-01-01")
        assert result["results"][0]["name"] == "Тест"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_get_events_server_error(httpx_mock, events_url):
    """Тест: если сервер вернул 500, клиент выбрасывает ошибку."""

    httpx_mock.add_response(
        url=events_url,
        method="GET",
        status_code=500
    )

    client = EventsProviderClient(httpx.AsyncClient(base_url=settings.api_base_url))
    try:
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_events(changed_at="2000-01-01")
    finally:   
        await client.close()


@pytest.mark.asyncio
async def test_get_seats_success():
    """Тест: клиент успешно получает места."""
    mock_client = AsyncMock()
    mock_client.get.return_value = Mock(
        json=lambda: {"seats": ["A1", "A2"]},
        raise_for_status=lambda: None,
    )

    client = EventsProviderClient(mock_client)

    result = await client.get_seats(uuid.uuid4())
    assert result["seats"] == ["A1", "A2"]


@pytest.mark.asyncio
async def test_register_success():
    """Тест: клиент успешно регистрирует пользователя."""
    mock_client = AsyncMock()
    mock_client.post.return_value = Mock(
        json=lambda: {"ticket_id": "abc-123"},
        raise_for_status=lambda: None,
    )

    client = EventsProviderClient(mock_client)

    result = await client.register(
        uuid.uuid4(), "Иван", "Петров", "A1", "ivan@example.com"
    )
    assert result["ticket_id"] == "abc-123"


@pytest.mark.asyncio
async def test_unregister_success():
    """Тест: клиент успешно отменяет регистрацию."""
    mock_client = AsyncMock()
    mock_client.request.return_value = Mock(
        json=lambda: {"success": True},
        raise_for_status=lambda: None,
    )

    client = EventsProviderClient(mock_client)

    result = await client.unregister(uuid.uuid4(), uuid.uuid4())
    assert result["success"] is True


@pytest.mark.asyncio
async def test_get_events_with_cursor():
    """Тест: клиент переходит по курсору (следующая страница)."""
    mock_client = AsyncMock()
    mock_client.send.return_value = Mock(
        json=lambda: {"results": [{"id": "1"}], "next": None},
        raise_for_status=lambda: None,
    )

    client = EventsProviderClient(mock_client)

    cursor = "https://events-provider.dev-2.python-labs.ru/api/events/?cursor=xyz"
    result = await client.get_events(cursor=cursor)
    assert result["results"] == [{"id": "1"}]
