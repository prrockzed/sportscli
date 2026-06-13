import pytest
import requests
from unittest.mock import MagicMock, call, patch

from sportscli import __version__
from sportscli.core.exceptions import ApiError, AuthError, NetworkError, RateLimitError
from sportscli.core.http import BaseAPIClient


# ---------------------------------------------------------------------------
# Concrete subclass used for testing the abstract base
# ---------------------------------------------------------------------------

class _Client(BaseAPIClient):
    BASE_URL = "https://api.test.example.com"


class MockResponse:
    def __init__(self, status_code: int, json_data: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.text = text

    def json(self):
        return self._json


@pytest.fixture
def client():
    return _Client()


# ---------------------------------------------------------------------------
# Session setup
# ---------------------------------------------------------------------------

class TestSessionSetup:
    def test_user_agent_header_contains_version(self, client):
        assert client.session.headers["User-Agent"] == f"sportscli/{__version__}"

    def test_session_is_requests_session(self, client):
        assert isinstance(client.session, requests.Session)


# ---------------------------------------------------------------------------
# _handle_response: status code → exception mapping
# ---------------------------------------------------------------------------

class TestHandleResponse:
    def test_200_returns_parsed_json(self, client):
        resp = MockResponse(200, {"key": "value"})
        assert client._handle_response(resp) == {"key": "value"}

    def test_401_raises_auth_error(self, client):
        with pytest.raises(AuthError) as exc_info:
            client._handle_response(MockResponse(401))
        assert exc_info.value.status_code == 401

    def test_403_raises_auth_error(self, client):
        with pytest.raises(AuthError) as exc_info:
            client._handle_response(MockResponse(403))
        assert exc_info.value.status_code == 403

    def test_429_raises_rate_limit_error(self, client):
        with pytest.raises(RateLimitError) as exc_info:
            client._handle_response(MockResponse(429))
        assert exc_info.value.status_code == 429

    def test_404_raises_api_error_not_auth_error(self, client):
        with pytest.raises(ApiError) as exc_info:
            client._handle_response(MockResponse(404, text="not found"))
        assert exc_info.value.status_code == 404
        assert not isinstance(exc_info.value, AuthError)

    def test_400_raises_api_error(self, client):
        with pytest.raises(ApiError) as exc_info:
            client._handle_response(MockResponse(400, text="bad request"))
        assert exc_info.value.status_code == 400

    def test_500_raises_api_error(self, client):
        with pytest.raises(ApiError) as exc_info:
            client._handle_response(MockResponse(500))
        assert exc_info.value.status_code == 500

    def test_503_raises_api_error(self, client):
        with pytest.raises(ApiError) as exc_info:
            client._handle_response(MockResponse(503))
        assert exc_info.value.status_code == 503

    def test_auth_error_message_mentions_api_key(self, client):
        with pytest.raises(AuthError) as exc_info:
            client._handle_response(MockResponse(401))
        assert "api key" in str(exc_info.value).lower()

    def test_rate_limit_error_message_is_helpful(self, client):
        with pytest.raises(RateLimitError) as exc_info:
            client._handle_response(MockResponse(429))
        assert "rate limit" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# get(): URL construction, params, retry logic
# ---------------------------------------------------------------------------

class TestGet:
    def test_builds_correct_url(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {})) as mock_get:
            client.get("/some/path")
        url = mock_get.call_args[0][0]
        assert url == "https://api.test.example.com/some/path"

    def test_returns_parsed_json_on_200(self, client):
        expected = {"result": "ok"}
        with patch.object(client.session, "get", return_value=MockResponse(200, expected)):
            result = client.get("/endpoint")
        assert result == expected

    def test_passes_params_to_session(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {})) as mock_get:
            client.get("/endpoint", params={"key": "val", "page": 1})
        assert mock_get.call_args[1]["params"] == {"key": "val", "page": 1}

    def test_passes_timeout_to_session(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {})) as mock_get:
            client.get("/endpoint")
        assert mock_get.call_args[1]["timeout"] == client.TIMEOUT

    @patch("sportscli.core.http.time.sleep")
    def test_retries_three_times_on_connection_error(self, mock_sleep, client):
        with patch.object(client.session, "get", side_effect=requests.ConnectionError("refused")) as mock_get:
            with pytest.raises(NetworkError):
                client.get("/endpoint")
            assert mock_get.call_count == 3

    @patch("sportscli.core.http.time.sleep")
    def test_retries_on_timeout(self, mock_sleep, client):
        with patch.object(client.session, "get", side_effect=requests.Timeout("timed out")) as mock_get:
            with pytest.raises(NetworkError):
                client.get("/endpoint")
            assert mock_get.call_count == 3

    @patch("sportscli.core.http.time.sleep")
    def test_sleeps_between_retries(self, mock_sleep, client):
        with patch.object(client.session, "get", side_effect=requests.ConnectionError()):
            with pytest.raises(NetworkError):
                client.get("/endpoint")
        # 3 attempts → 2 sleeps (no sleep after final attempt)
        assert mock_sleep.call_count == 2

    @patch("sportscli.core.http.time.sleep")
    def test_exponential_backoff_sleep_values(self, mock_sleep, client):
        with patch.object(client.session, "get", side_effect=requests.ConnectionError()):
            with pytest.raises(NetworkError):
                client.get("/endpoint")
        sleep_args = [c[0][0] for c in mock_sleep.call_args_list]
        assert sleep_args == [1, 2]  # 2^0, 2^1

    @patch("sportscli.core.http.time.sleep")
    def test_succeeds_on_second_attempt(self, mock_sleep, client):
        expected = {"retry": "success"}
        responses = [requests.ConnectionError("fail"), MockResponse(200, expected)]
        with patch.object(client.session, "get", side_effect=responses):
            result = client.get("/endpoint")
        assert result == expected
        assert mock_sleep.call_count == 1

    def test_no_retry_on_http_error(self, client):
        """4xx/5xx errors come back as responses, not exceptions — no retry."""
        with patch.object(client.session, "get", return_value=MockResponse(500)) as mock_get:
            with pytest.raises(ApiError):
                client.get("/endpoint")
        assert mock_get.call_count == 1

    @patch("sportscli.core.http.time.sleep")
    def test_raises_network_error_after_all_retries(self, mock_sleep, client):
        with patch.object(client.session, "get", side_effect=requests.ConnectionError("final")):
            with pytest.raises(NetworkError):
                client.get("/endpoint")
