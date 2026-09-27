class application_error(Exception):
    """Базовое исключение приложения."""


class validation_error(application_error):
    """Исключение, возникающее при некорректных данных."""
