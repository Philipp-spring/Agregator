from unittest.mock import AsyncMock

import pytest

from app.clients.paginator import EventsPaginator
from app.clients.provider import EventsProviderClient


@pytest.mark.asyncio
async def test_paginator_iterates_over_all_pages():
    """Тест: пагинатор должен собрать события со всех страниц."""

    mock_client = AsyncMock(spec=EventsProviderClient)

    mock_client.get_events.side_effect = [
        {
            "results": [{"id": "event-1", "name": "Событие 1"}],
            "next": "http://next-page-url"
        },
        {
            "results": [{"id": "event-2", "name": "Событие 2"}],
            "next": None
        }
    ]

    paginator = EventsPaginator(mock_client, changed_at="2000-01-01")

    events = [event async for event in paginator]

    assert len(events) == 2
    assert events[0]["id"] == "event-1"
    assert events[1]["id"] == "event-2"

    assert mock_client.get_events.call_count == 2
    mock_client.get_events.assert_any_call(changed_at="2000-01-01")
    mock_client.get_events.assert_any_call(cursor="http://next-page-url")
