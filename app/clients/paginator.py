from app.clients.provider import EventsProviderClient


class EventsPaginator:
    """Итератор для постраничного получения событий из API."""

    def __init__(self, client: EventsProviderClient, changed_at: str = "2000-01-01"):
        self.client = client
        self.changed_at = changed_at

    async def __aiter__(self):
        """Асинхронный итератор, который отдает события по одному."""
        cursor = None
        is_first_page = True
        current_page = 0
        max_pages = 500

        while current_page < max_pages:
            current_page += 1

            if is_first_page:
                data = await self.client.get_events(changed_at=self.changed_at)
                is_first_page = False
            else:
                data = await self.client.get_events(cursor=cursor)

            events_data = data.get("results", [])
            if not events_data:
                break

            cursor = data.get("next")

            for event in events_data:
                yield event

            if not cursor:
                break
