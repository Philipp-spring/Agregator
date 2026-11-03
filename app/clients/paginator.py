from app.clients.provider import EventsProviderClient


class EventsPaginator:
    """Итератор для постраничного получения событий из API."""

    def __init__(self, client: EventsProviderClient, changed_at: str = "2000-01-01"):
        self.client = client
        self.changed_at = changed_at
        self.cursor = None
        self.is_first_page = True
        self.max_pages = 500
        self.current_page = 0

    async def __aiter__(self):
        """Асинхронный итератор, который отдает события по одному."""
        while self.current_page < self.max_pages:
            self.current_page += 1

            if self.is_first_page:
                data = await self.client.get_events(changed_at=self.changed_at)
                self.is_first_page = False
            else:
                data = await self.client.get_events(cursor=self.cursor)

            events_data = data.get("results", [])
            if not events_data:
                break

            for event in events_data:
                yield event

            self.cursor = data.get("next")
            if not self.cursor:
                break
