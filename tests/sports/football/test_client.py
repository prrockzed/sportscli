import pytest
from unittest.mock import patch

from sportscli.sports.football.client import LEAGUE_IDS, FootballDataClient


class MockResponse:
    def __init__(self, status_code: int, json_data=None, text: str = ""):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.text = text

    def json(self):
        return self._json


@pytest.fixture
def client():
    return FootballDataClient(api_key="test-football-key")


class TestFootballDataClientSetup:
    def test_base_url_is_football_data(self, client):
        assert "football-data.org" in client.BASE_URL

    def test_api_key_set_as_auth_header(self, client):
        assert client.session.headers.get("X-Auth-Token") == "test-football-key"

    def test_different_keys_produce_different_headers(self):
        c1 = FootballDataClient(api_key="key-one")
        c2 = FootballDataClient(api_key="key-two")
        assert c1.session.headers["X-Auth-Token"] == "key-one"
        assert c2.session.headers["X-Auth-Token"] == "key-two"


class TestLeagueIdMapping:
    def test_pl_maps_to_PL(self):
        assert LEAGUE_IDS["pl"] == "PL"

    def test_bl1_maps_to_BL1(self):
        assert LEAGUE_IDS["bl1"] == "BL1"

    def test_sa_maps_to_SA(self):
        assert LEAGUE_IDS["sa"] == "SA"

    def test_pd_maps_to_PD(self):
        assert LEAGUE_IDS["pd"] == "PD"

    def test_fl1_maps_to_FL1(self):
        assert LEAGUE_IDS["fl1"] == "FL1"

    def test_ucl_maps_to_CL(self):
        assert LEAGUE_IDS["ucl"] == "CL"

    def test_all_values_are_uppercase(self):
        for competition_id in LEAGUE_IDS.values():
            assert competition_id == competition_id.upper()


class TestGetLiveMatches:
    def test_calls_matches_endpoint(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"matches": []})) as mock_get:
            client.get_live_matches()
        assert "/matches" in mock_get.call_args[0][0]

    def test_filters_for_live_status(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"matches": []})) as mock_get:
            client.get_live_matches()
        params = mock_get.call_args[1]["params"]
        assert params.get("status") == "LIVE"

    def test_returns_matches_data(self, client):
        payload = {"matches": [{"id": 1, "status": "IN_PLAY"}]}
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)):
            result = client.get_live_matches()
        assert result == payload


class TestGetStandings:
    def test_uses_mapped_competition_id_for_pl(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"standings": []})) as mock_get:
            client.get_standings("pl")
        assert "/PL/" in mock_get.call_args[0][0]

    def test_uses_mapped_competition_id_for_ucl(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"standings": []})) as mock_get:
            client.get_standings("ucl")
        assert "/CL/" in mock_get.call_args[0][0]

    def test_unknown_code_is_uppercased(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"standings": []})) as mock_get:
            client.get_standings("xyz")
        assert "/XYZ/" in mock_get.call_args[0][0]

    def test_case_insensitive_code_lookup(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"standings": []})) as mock_get:
            client.get_standings("PL")
        assert "/PL/" in mock_get.call_args[0][0]

    def test_calls_standings_endpoint(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"standings": []})) as mock_get:
            client.get_standings("pl")
        assert "standings" in mock_get.call_args[0][0]


class TestGetFixtures:
    def test_uses_mapped_competition_id(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"matches": []})) as mock_get:
            client.get_fixtures("sa")
        assert "/SA/" in mock_get.call_args[0][0]

    def test_filters_for_scheduled_matches(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {"matches": []})) as mock_get:
            client.get_fixtures("pl")
        params = mock_get.call_args[1]["params"]
        assert params.get("status") == "SCHEDULED"

    def test_returns_fixtures_data(self, client):
        payload = {"matches": [{"id": 99, "status": "SCHEDULED"}]}
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)):
            result = client.get_fixtures("pl")
        assert result == payload
