from enum import StrEnum


class EventStatus(StrEnum):
    """Статусы события (по документации провайдера)."""

    NEW = "new"
    PUBLISHED = "published"
    REGISTRATION_CLOSED = "registration_closed"
    FINISHED = "finished"


class SyncStatus(StrEnum):
    """Статусы синхронизации."""

    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
