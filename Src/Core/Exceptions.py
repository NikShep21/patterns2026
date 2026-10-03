class application_error(Exception):
    """Базовое исключение приложения."""


class validation_error(application_error):
    """Исключение, возникающее при некорректных данных."""


class operation_error(application_error):
    """Исключение, возникающее при ошибке выполнения операции."""
