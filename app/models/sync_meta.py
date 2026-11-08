from datetime import datetime

from sqlalchemy import DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import SyncStatus


class SyncMetadata(Base):
    __tablename__ = "sync_metadata"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    last_sync_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_status: Mapped[SyncStatus] = mapped_column(Enum(SyncStatus, native_enum=False, length=50), default=SyncStatus.IDLE)
