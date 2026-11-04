import httpx
import pytest

from app.clients.provider import EventsProviderClient


@pytest.mark.asyncio
async def test_get_events_success(httpx_mock):
    """Тест: клиент успешно делает запрос и возвращает JSON."""
    
    # Меняем URL на тот, который сейчас в config.py
    httpx_mock.add_response(
        url="http://student-system-events-provider-web.student-system-events-provider.svc:8000/api/events/?changed_at=2000-01-01",
        method="GET",
        json={"results": [{"id": "1", "name": "Тест"}], "next": None},
        status_code=200
    )

    client = EventsProviderClient()
    result = await client.get_events(changed_at="2000-01-01")
    assert result["results"][0]["name"] == "Тест"
    await client.close()


@pytest.mark.asyncio
async def test_get_events_server_error(httpx_mock):
    """Тест: если сервер вернул 500, клиент выбрасывает ошибку."""

    # Меняем URL на тот, который сейчас в config.py
    httpx_mock.add_response(
        url="http://student-system-events-provider-web.student-system-events-provider.svc:8000/api/events/?changed_at=2000-01-01",
        method="GET",
        status_code=500
    )

    client = EventsProviderClient()

    with pytest.raises(httpx.HTTPStatusError):
        await client.get_events(changed_at="2000-01-01")
        
    await client.close()
