import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums import EventStatus


class PlaceShortOut(BaseModel):
    """Площадка для списка (без seats_pattern)"""

    id: uuid.UUID
    name: str
    city: str
    address: str

    model_config = ConfigDict(from_attributes=True)


class PlaceOut(PlaceShortOut):
    """Площадка для деталей (с seats_pattern)"""

    seats_pattern: str


class EventOut(BaseModel):
    """Событие для списка (использует PlaceShortOut)"""

    id: uuid.UUID
    name: str
    place: PlaceShortOut
    event_time: datetime
    registration_deadline: datetime
    status: EventStatus
    number_of_visitors: int

    model_config = ConfigDict(from_attributes=True)


class EventDetailOut(EventOut):
    """Событие для деталей (использует PlaceOut)"""

    place: PlaceOut


class PaginatedEventOut(BaseModel):
    """Список событий с пагинацией"""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[EventOut]


class EventSeatsOut(BaseModel):
    """Свободные места на событие"""

    event_id: uuid.UUID
    available_seats: list[str]
