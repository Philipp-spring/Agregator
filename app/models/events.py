import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, Enum, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import EventStatus


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name: Mapped[str]
    place_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("places.id"))
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus, native_enum=False, length=50), default=EventStatus.NEW)
    number_of_visitors: Mapped[int] = mapped_column(server_default=text("0"))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    place: Mapped["Place"] = relationship("Place", back_populates="events", lazy="joined")

    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="event")
