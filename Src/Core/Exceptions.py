class application_error(Exception):
    """Базовое исключение приложения."""


class validation_error(application_error):
    """Исключение, возникающее при некорректных данных."""


class operation_error(application_error):
    """Исключение, возникающее при ошибке выполнения операции."""


class entity_conflict_error(application_error):
    """Изменение конфликтует с существующей записью или связью."""


class entity_not_found_error(application_error):
    """Запись с указанным кодом отсутствует в коллекции."""
