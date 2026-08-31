class ApplicationError(Exception):
    """Base error raised by application use cases."""


class ResourceNotFoundError(ApplicationError):
    """Raised when a requested application resource does not exist."""

