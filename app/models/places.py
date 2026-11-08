import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    city: Mapped[str]
    address: Mapped[str]
    seats_pattern: Mapped[str]

    events: Mapped[list["Event"]] = relationship("Event", back_populates="place")
