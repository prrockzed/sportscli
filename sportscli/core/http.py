import time
from abc import ABC, abstractmethod

import requests

from sportscli import __version__
from sportscli.core.exceptions import (
    ApiError,
    AuthError,
    NetworkError,
    RateLimitError,
)


class BaseAPIClient(ABC):
    BASE_URL: str
    TIMEOUT: int = 10
    MAX_RETRIES: int = 3

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": f"sportscli/{__version__}"})

    @property
    @abstractmethod
    def BASE_URL(self) -> str:  # type: ignore[override]
        ...

    def get(self, endpoint: str, params: dict | None = None) -> dict | list:
        url = f"{self.BASE_URL}{endpoint}"
        last_error: Exception | None = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(url, params=params, timeout=self.TIMEOUT)
                return self._handle_response(response)
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_error = exc
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2**attempt)

        raise NetworkError(str(last_error)) from last_error

    def _handle_response(self, response: requests.Response) -> dict:
        status = response.status_code

        if status == 200:
            return response.json()
        if status in (401, 403):
            raise AuthError(
                f"Authentication failed ({status}): check your API key.", status
            )
        if status == 429:
            raise RateLimitError(
                "Rate limit exceeded. Please wait before retrying.", status
            )
        if 400 <= status < 500:
            raise ApiError(f"Client error {status}: {response.text[:200]}", status)
        if status >= 500:
            raise ApiError(f"Server error {status}: the API is having issues.", status)

        return response.json()
