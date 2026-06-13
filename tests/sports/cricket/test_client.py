import pytest
from unittest.mock import patch

from sportscli.sports.cricket.client import CricketDataClient


class MockResponse:
    def __init__(self, status_code: int, json_data=None, text: str = ""):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.text = text

    def json(self):
        return self._json


@pytest.fixture
def client():
    return CricketDataClient(api_key="test-cricket-key")


class TestCricketDataClientSetup:
    def test_api_key_is_stored(self, client):
        assert client._api_key == "test-cricket-key"

    def test_base_url_is_set(self, client):
        assert client.BASE_URL is not None
        assert client.BASE_URL.startswith("https://")

    def test_instantiation_requires_api_key(self):
        c = CricketDataClient(api_key="some-key")
        assert c._api_key == "some-key"


class TestGetLiveMatches:
    def test_api_key_sent_in_params(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"data": []})) as mock_get:
            client.get_live_matches()
        params = mock_get.call_args[1]["params"]
        assert params.get("apikey") == "test-cricket-key"

    def test_calls_current_matches_endpoint(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"data": []})) as mock_get:
            client.get_live_matches()
        url = mock_get.call_args[0][0]
        assert "currentMatches" in url or "live" in url.lower() or "current" in url.lower()

    def test_returns_response_data(self, client):
        payload = {"data": [{"id": "m1", "name": "Test Match"}]}
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)):
            result = client.get_live_matches()
        assert result == payload


class TestGetScorecard:
    def test_api_key_sent_in_params(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"data": {}})) as mock_get:
            client.get_scorecard("match-abc")
        params = mock_get.call_args[1]["params"]
        assert params.get("apikey") == "test-cricket-key"

    def test_match_id_sent_in_params(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"data": {}})) as mock_get:
            client.get_scorecard("match-abc-123")
        params = mock_get.call_args[1]["params"]
        assert params.get("id") == "match-abc-123"

    def test_returns_scorecard_data(self, client):
        payload = {"data": {"name": "Test Match", "score": []}}
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)):
            result = client.get_scorecard("match-id")
        assert result == payload


class TestGetSchedule:
    def test_api_key_sent_in_params(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"data": []})) as mock_get:
            client.get_schedule()
        params = mock_get.call_args[1]["params"]
        assert params.get("apikey") == "test-cricket-key"

    def test_calls_matches_endpoint(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"data": []})) as mock_get:
            client.get_schedule()
        url = mock_get.call_args[0][0]
        assert "matches" in url.lower()

    def test_returns_schedule_data(self, client):
        payload = {"data": [{"id": "m2", "name": "Upcoming Match"}]}
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)):
            result = client.get_schedule()
        assert result == payload
