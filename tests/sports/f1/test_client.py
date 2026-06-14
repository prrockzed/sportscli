from unittest.mock import patch

from sportscli.sports.f1.client import F1Client, OpenF1Client


class MockResponse:
    def __init__(self, status_code: int, json_data=None, text: str = ""):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.text = text

    def json(self):
        return self._json


@staticmethod
def _empty_mrdata():
    return {"MRData": {"RaceTable": {"Races": []}, "StandingsTable": {"StandingsLists": []}}}


# ---------------------------------------------------------------------------
# F1Client
# ---------------------------------------------------------------------------

class TestF1ClientSetup:
    def test_base_url_contains_jolpica(self):
        assert "jolpi.ca" in F1Client.BASE_URL

    def test_base_url_contains_ergast(self):
        assert "ergast" in F1Client.BASE_URL

    def test_client_instantiates(self):
        client = F1Client()
        assert client is not None


class TestF1ClientGetSchedule:
    def test_calls_races_endpoint(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_schedule()
        assert "races.json" in mock_get.call_args[0][0]

    def test_default_season_is_current(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_schedule()
        assert "/current/" in mock_get.call_args[0][0]

    def test_custom_season_is_used(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_schedule(season="2023")
        assert "/2023/" in mock_get.call_args[0][0]

    def test_returns_dict(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)):
            result = client.get_schedule()
        assert isinstance(result, dict)


class TestF1ClientGetDriverStandings:
    def test_calls_driver_standings_endpoint(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_driver_standings()
        assert "driverStandings.json" in mock_get.call_args[0][0]

    def test_default_season_is_current(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_driver_standings()
        assert "/current/" in mock_get.call_args[0][0]

    def test_custom_season_is_used(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_driver_standings(season="2022")
        assert "/2022/" in mock_get.call_args[0][0]


class TestF1ClientGetConstructorStandings:
    def test_calls_constructor_standings_endpoint(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_constructor_standings()
        assert "constructorStandings.json" in mock_get.call_args[0][0]

    def test_default_season_is_current(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_constructor_standings()
        assert "/current/" in mock_get.call_args[0][0]


class TestF1ClientGetRaceResults:
    def test_calls_results_endpoint(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_race_results()
        assert "results.json" in mock_get.call_args[0][0]

    def test_default_round_is_last(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_race_results()
        assert "/last/" in mock_get.call_args[0][0]

    def test_custom_round_is_used(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_race_results(season="2024", round="5")
        assert "/5/" in mock_get.call_args[0][0]
        assert "/2024/" in mock_get.call_args[0][0]

    def test_default_season_is_current(self):
        client = F1Client()
        payload = _empty_mrdata()
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)) as mock_get:
            client.get_race_results()
        assert "/current/" in mock_get.call_args[0][0]


# ---------------------------------------------------------------------------
# OpenF1Client
# ---------------------------------------------------------------------------

class TestOpenF1ClientSetup:
    def test_base_url_contains_openf1(self):
        assert "openf1.org" in OpenF1Client.BASE_URL

    def test_client_instantiates(self):
        client = OpenF1Client()
        assert client is not None


class TestOpenF1ClientGetLatestSession:
    def test_calls_sessions_endpoint(self):
        client = OpenF1Client()
        with patch.object(client.session, "get", return_value=MockResponse(200, [])) as mock_get:
            client.get_latest_session()
        assert "/sessions" in mock_get.call_args[0][0]

    def test_passes_latest_session_key(self):
        client = OpenF1Client()
        with patch.object(client.session, "get", return_value=MockResponse(200, [])) as mock_get:
            client.get_latest_session()
        params = mock_get.call_args[1]["params"]
        assert params.get("session_key") == "latest"

    def test_returns_list(self):
        client = OpenF1Client()
        payload = [{"session_key": 9999, "session_name": "Race"}]
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)):
            result = client.get_latest_session()
        assert isinstance(result, list)
        assert result[0]["session_key"] == 9999


class TestOpenF1ClientGetPositions:
    def test_calls_position_endpoint(self):
        client = OpenF1Client()
        with patch.object(client.session, "get", return_value=MockResponse(200, [])) as mock_get:
            client.get_positions(9999)
        assert "/position" in mock_get.call_args[0][0]

    def test_passes_session_key(self):
        client = OpenF1Client()
        with patch.object(client.session, "get", return_value=MockResponse(200, [])) as mock_get:
            client.get_positions(9999)
        params = mock_get.call_args[1]["params"]
        assert params.get("session_key") == 9999

    def test_returns_list(self):
        client = OpenF1Client()
        payload = [{"driver_number": 1, "position": 1}]
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)):
            result = client.get_positions(9999)
        assert isinstance(result, list)


class TestOpenF1ClientGetDrivers:
    def test_calls_drivers_endpoint(self):
        client = OpenF1Client()
        with patch.object(client.session, "get", return_value=MockResponse(200, [])) as mock_get:
            client.get_drivers(9999)
        assert "/drivers" in mock_get.call_args[0][0]

    def test_passes_session_key(self):
        client = OpenF1Client()
        with patch.object(client.session, "get", return_value=MockResponse(200, [])) as mock_get:
            client.get_drivers(9999)
        params = mock_get.call_args[1]["params"]
        assert params.get("session_key") == 9999

    def test_returns_list(self):
        client = OpenF1Client()
        payload = [{"driver_number": 1, "name_acronym": "VER", "team_name": "Red Bull Racing"}]
        with patch.object(client.session, "get", return_value=MockResponse(200, payload)):
            result = client.get_drivers(9999)
        assert isinstance(result, list)
        assert result[0]["name_acronym"] == "VER"
