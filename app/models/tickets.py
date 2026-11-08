import uuid

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"))
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    seat: Mapped[str]

    event: Mapped["Event"] = relationship("Event", back_populates="tickets")
