import pytest
from unittest.mock import patch
from typer.testing import CliRunner

from sportscli.core.exceptions import ApiError, NetworkError
from sportscli.sports.f1.app import app

runner = CliRunner()

_EMPTY_SCHEDULE = {"MRData": {"RaceTable": {"season": "2025", "Races": []}}}
_EMPTY_DRIVER_STANDINGS = {
    "MRData": {"StandingsTable": {"StandingsLists": [{"season": "2025", "round": "10", "DriverStandings": []}]}}
}
_EMPTY_CONSTRUCTOR_STANDINGS = {
    "MRData": {"StandingsTable": {"StandingsLists": [{"season": "2025", "round": "10", "ConstructorStandings": []}]}}
}
_EMPTY_RESULTS = {"MRData": {"RaceTable": {"Races": []}}}
_SESSION = [{"session_key": 9999, "session_name": "Race", "session_type": "Race", "location": "Monaco", "country_name": "Monaco"}]


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))


@pytest.fixture
def mock_f1_client():
    with patch("sportscli.sports.f1.app.F1Client") as MockClient:
        instance = MockClient.return_value
        instance.get_schedule.return_value = _EMPTY_SCHEDULE
        instance.get_driver_standings.return_value = _EMPTY_DRIVER_STANDINGS
        instance.get_constructor_standings.return_value = _EMPTY_CONSTRUCTOR_STANDINGS
        instance.get_race_results.return_value = _EMPTY_RESULTS
        yield instance


@pytest.fixture
def mock_openf1_client():
    with patch("sportscli.sports.f1.app.OpenF1Client") as MockClient:
        instance = MockClient.return_value
        instance.get_latest_session.return_value = _SESSION
        instance.get_positions.return_value = []
        instance.get_drivers.return_value = []
        yield instance


# ---------------------------------------------------------------------------
# schedule
# ---------------------------------------------------------------------------

class TestScheduleCommand:
    def test_exits_0_on_success(self, mock_f1_client):
        result = runner.invoke(app, ["schedule"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_f1_client):
        mock_f1_client.get_schedule.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["schedule"])
        assert result.exit_code == 1

    def test_network_error_message_shown(self, mock_f1_client):
        mock_f1_client.get_schedule.side_effect = NetworkError("no route")
        result = runner.invoke(app, ["schedule"])
        assert "Network error" in result.output

    def test_exits_1_on_api_error(self, mock_f1_client):
        mock_f1_client.get_schedule.side_effect = ApiError("server error", 500)
        result = runner.invoke(app, ["schedule"])
        assert result.exit_code == 1

    def test_api_error_message_shown(self, mock_f1_client):
        mock_f1_client.get_schedule.side_effect = ApiError("bad request", 400)
        result = runner.invoke(app, ["schedule"])
        assert "API error" in result.output

    def test_shows_no_schedule_when_empty(self, mock_f1_client):
        result = runner.invoke(app, ["schedule"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# standings
# ---------------------------------------------------------------------------

class TestStandingsCommand:
    def test_exits_0_on_success(self, mock_f1_client):
        result = runner.invoke(app, ["standings"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_f1_client):
        mock_f1_client.get_driver_standings.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["standings"])
        assert result.exit_code == 1

    def test_exits_1_on_api_error(self, mock_f1_client):
        mock_f1_client.get_driver_standings.side_effect = ApiError("not found", 404)
        result = runner.invoke(app, ["standings"])
        assert result.exit_code == 1

    def test_shows_driver_standings_data(self, mock_f1_client):
        mock_f1_client.get_driver_standings.return_value = {
            "MRData": {
                "StandingsTable": {
                    "StandingsLists": [{
                        "season": "2025",
                        "round": "10",
                        "DriverStandings": [{
                            "position": "1",
                            "points": "250",
                            "wins": "8",
                            "Driver": {
                                "givenName": "Max",
                                "familyName": "Verstappen",
                                "nationality": "Dutch",
                            },
                            "Constructors": [{"name": "Red Bull Racing"}],
                        }],
                    }]
                }
            }
        }
        result = runner.invoke(app, ["standings"])
        assert result.exit_code == 0
        assert "Verstappen" in result.output


# ---------------------------------------------------------------------------
# constructors
# ---------------------------------------------------------------------------

class TestConstructorsCommand:
    def test_exits_0_on_success(self, mock_f1_client):
        result = runner.invoke(app, ["constructors"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_f1_client):
        mock_f1_client.get_constructor_standings.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["constructors"])
        assert result.exit_code == 1

    def test_exits_1_on_api_error(self, mock_f1_client):
        mock_f1_client.get_constructor_standings.side_effect = ApiError("server error", 500)
        result = runner.invoke(app, ["constructors"])
        assert result.exit_code == 1

    def test_shows_constructor_data(self, mock_f1_client):
        mock_f1_client.get_constructor_standings.return_value = {
            "MRData": {
                "StandingsTable": {
                    "StandingsLists": [{
                        "season": "2025",
                        "round": "10",
                        "ConstructorStandings": [{
                            "position": "1",
                            "points": "450",
                            "wins": "10",
                            "Constructor": {"name": "Red Bull Racing", "nationality": "Austrian"},
                        }],
                    }]
                }
            }
        }
        result = runner.invoke(app, ["constructors"])
        assert result.exit_code == 0
        assert "Red Bull Racing" in result.output


# ---------------------------------------------------------------------------
# results
# ---------------------------------------------------------------------------

class TestResultsCommand:
    def test_exits_0_on_success(self, mock_f1_client):
        mock_f1_client.get_race_results.return_value = {
            "MRData": {
                "RaceTable": {
                    "Races": [{
                        "raceName": "Monaco Grand Prix",
                        "date": "2025-05-25",
                        "Circuit": {"circuitName": "Circuit de Monaco"},
                        "Results": [],
                    }]
                }
            }
        }
        result = runner.invoke(app, ["results"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_f1_client):
        mock_f1_client.get_race_results.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["results"])
        assert result.exit_code == 1

    def test_exits_1_on_api_error(self, mock_f1_client):
        mock_f1_client.get_race_results.side_effect = ApiError("not found", 404)
        result = runner.invoke(app, ["results"])
        assert result.exit_code == 1

    def test_no_results_message_when_empty(self, mock_f1_client):
        result = runner.invoke(app, ["results"])
        assert result.exit_code == 0

    def test_shows_race_name_in_output(self, mock_f1_client):
        mock_f1_client.get_race_results.return_value = {
            "MRData": {
                "RaceTable": {
                    "Races": [{
                        "raceName": "British Grand Prix",
                        "date": "2025-07-06",
                        "Circuit": {"circuitName": "Silverstone"},
                        "Results": [
                            {
                                "position": "1",
                                "points": "25",
                                "grid": "1",
                                "laps": "52",
                                "status": "Finished",
                                "Driver": {"givenName": "Lewis", "familyName": "Hamilton"},
                                "Constructor": {"name": "Mercedes"},
                                "Time": {"time": "1:30:00.000"},
                            }
                        ],
                    }]
                }
            }
        }
        result = runner.invoke(app, ["results"])
        assert result.exit_code == 0
        assert "British Grand Prix" in result.output
        assert "Hamilton" in result.output


# ---------------------------------------------------------------------------
# live
# ---------------------------------------------------------------------------

class TestLiveCommand:
    def test_exits_0_on_success(self, mock_openf1_client):
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_openf1_client):
        mock_openf1_client.get_latest_session.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 1

    def test_network_error_message_shown(self, mock_openf1_client):
        mock_openf1_client.get_latest_session.side_effect = NetworkError("no route")
        result = runner.invoke(app, ["live"])
        assert "Network error" in result.output

    def test_exits_1_on_api_error(self, mock_openf1_client):
        mock_openf1_client.get_latest_session.side_effect = ApiError("server error", 500)
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 1

    def test_exits_1_when_no_session_data(self, mock_openf1_client):
        mock_openf1_client.get_latest_session.return_value = []
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 1

    def test_shows_session_name(self, mock_openf1_client):
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 0
        assert "Race" in result.output

    def test_shows_location(self, mock_openf1_client):
        result = runner.invoke(app, ["live"])
        assert "Monaco" in result.output

    def test_positions_fetched_with_session_key(self, mock_openf1_client):
        runner.invoke(app, ["live"])
        mock_openf1_client.get_positions.assert_called_once_with(9999)

    def test_drivers_fetched_with_session_key(self, mock_openf1_client):
        runner.invoke(app, ["live"])
        mock_openf1_client.get_drivers.assert_called_once_with(9999)

    def test_shows_driver_acronym_in_output(self, mock_openf1_client):
        mock_openf1_client.get_positions.return_value = [
            {"driver_number": 1, "position": 1}
        ]
        mock_openf1_client.get_drivers.return_value = [
            {"driver_number": 1, "name_acronym": "VER", "team_name": "Red Bull Racing"}
        ]
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 0
        assert "VER" in result.output
