from uuid import UUID

import httpx

from app.config import settings


class EventsProviderClient:
    def __init__(self):

        self.client = httpx.AsyncClient(
            base_url=settings.api_base_url,
            headers={"x-api-key": settings.api_key},
            timeout=httpx.Timeout(10.0, connect=5.0)
        )


    async def get_events(self, changed_at: str = "2000-01-01", cursor: str | None = None):
        """Получение мероприятий от внешнего API"""
        if cursor:
            if "events-provider" in cursor:
                cursor = cursor.replace("https://events-provider.dev-2.python-labs.ru",  settings.api_base_url)
                cursor = cursor.replace("http://events-provider.dev-2.python-labs.ru", settings.api_base_url)


            req = self.client.build_request("GET", cursor)
            response = await self.client.send(req)

        else:
            response = await self.client.get("/api/events/", params={"changed_at": changed_at})

        response.raise_for_status()
        return response.json()


    async def get_seats(self, event_id: UUID):
        """Получение свободных мест для конкретного мероприятия от внешнего API"""
        response = await self.client.get(f"/api/events/{event_id}/seats/")
        response.raise_for_status()
        return response.json()


    async def register(self, event_id: UUID, first_name: str, last_name: str, seat: str, email: str):
        """Регистрация пользователя на мероприятие"""
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "seat": seat,
            "email": email
        }
        response = await self.client.post(f"/api/events/{event_id}/register/", json=data)
        response.raise_for_status()
        return response.json()



    async def unregister(self, event_id: UUID, ticket_id: UUID):
        """отмена регистрации / аннулирование билета"""

        data = {"ticket_id": str(ticket_id)}
        response = await self.client.request("DELETE", f"/api/events/{event_id}/unregister/", json=data)


        response.raise_for_status()
        return response.json()


    async def close(self):
        """Метод для закрытия соединений в пуле соединений (вызывается при выключении сервера)"""
        await self.client.aclose()


    async def __aenter__(self):
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
