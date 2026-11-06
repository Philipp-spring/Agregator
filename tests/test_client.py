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

    client = EventsProviderClient()
    result = await client.get_events(changed_at="2000-01-01")
    assert result["results"][0]["name"] == "Тест"
    await client.close()


@pytest.mark.asyncio
async def test_get_events_server_error(httpx_mock, events_url):
    """Тест: если сервер вернул 500, клиент выбрасывает ошибку."""

    httpx_mock.add_response(
        url=events_url,
        method="GET",
        status_code=500
    )

    client = EventsProviderClient()

    with pytest.raises(httpx.HTTPStatusError):
        await client.get_events(changed_at="2000-01-01")
        
    await client.close()
