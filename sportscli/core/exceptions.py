class SportsCLIError(Exception):
    """Base exception for all sportscli errors."""


class NetworkError(SportsCLIError):
    """Raised on connection timeout or DNS failure."""


class ConfigError(SportsCLIError):
    """Raised on missing config or bad key format."""


class ApiError(SportsCLIError):
    """Raised when the API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AuthError(ApiError):
    """Raised on 401 or 403 responses."""


class RateLimitError(ApiError):
    """Raised on 429 responses."""
