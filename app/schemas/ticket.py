import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TicketCreate(BaseModel):
    """Запрос на регистрацию (от пользователя)"""

    event_id: uuid.UUID
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    seat: str = Field(min_length=1, max_length=10, pattern=r"^[A-Za-z]\d+$")


class TicketOut(BaseModel):
    """Ответ с данными билета (пользователю)"""

    ticket_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
