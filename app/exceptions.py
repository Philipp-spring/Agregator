class DomainError(Exception):
    """Базовое доменное исключение"""


class EventNotFoundError(DomainError):
    """Событие не найдено в базе данных"""


class EventNotPublishedError(DomainError):
    """Событие не опубликовано (регистрация недоступна)"""


class RegistrationDeadlinePassedError(DomainError):
    """Срок регистрации на событие истёк"""


class SeatNotAvailableError(DomainError):
    """Выбранное место занято или не существует"""


class TicketIdMissingError(DomainError):
    """Внешний API не вернул ticket_id при регистрации"""


class ProviderError(DomainError):
    """Ошибка при обращении к внешнему API провайдера"""


class TicketNotFoundError(DomainError):
    """Билет не найден в базе данных"""
