class DomainError(Exception):
    """Базовое доменное исключение"""
    pass


class EventNotFoundError(DomainError):
    """Событие не найдено в базе данных"""
    pass


class EventNotPublishedError(DomainError):
    """Событие не опубликовано (регистрация недоступна)"""
    pass


class RegistrationDeadlinePassedError(DomainError):
    """Срок регистрации на событие истёк"""
    pass


class SeatNotAvailableError(DomainError):
    """Выбранное место занято или не существует"""
    pass


class TicketIdMissingError(DomainError):
    """Внешний API не вернул ticket_id при регистрации"""
    pass


class ProviderError(DomainError):
    """Ошибка при обращении к внешнему API провайдера"""
    pass
