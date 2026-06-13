import pytest
from unittest.mock import patch
from typer.testing import CliRunner

from sportscli.core.exceptions import ApiError, AuthError, NetworkError
from sportscli.sports.football.app import app

runner = CliRunner()

_STORED_KEY = "stored-football-key"
_EMPTY_STANDINGS = {"standings": [], "competition": {"name": "Premier League"}}
_EMPTY_FIXTURES = {"matches": [], "competition": {"name": "Premier League"}}


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))


@pytest.fixture
def with_key():
    with patch("sportscli.sports.football.app.config.get_api_key", return_value=_STORED_KEY):
        yield


@pytest.fixture
def mock_client(with_key):
    with patch("sportscli.sports.football.app.FootballDataClient") as MockClient:
        instance = MockClient.return_value
        instance.get_live_matches.return_value = {"matches": []}
        instance.get_standings.return_value = _EMPTY_STANDINGS
        instance.get_fixtures.return_value = _EMPTY_FIXTURES
        yield instance


class TestLiveCommand:
    def test_exits_0_on_success(self, mock_client):
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_client):
        mock_client.get_live_matches.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 1

    def test_network_error_message_shown(self, mock_client):
        mock_client.get_live_matches.side_effect = NetworkError("no route")
        result = runner.invoke(app, ["live"])
        assert "Network error" in result.output

    def test_exits_1_on_auth_error(self, mock_client):
        mock_client.get_live_matches.side_effect = AuthError("unauthorized", 401)
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 1

    def test_auth_error_suggests_config_set(self, mock_client):
        mock_client.get_live_matches.side_effect = AuthError("forbidden", 403)
        result = runner.invoke(app, ["live"])
        assert "config set football" in result.output

    def test_prompts_for_key_when_none_stored(self):
        with patch("sportscli.sports.football.app.config.get_api_key", return_value=None):
            with patch("sportscli.sports.football.app.FootballDataClient") as MockClient:
                MockClient.return_value.get_live_matches.return_value = {"matches": []}
                result = runner.invoke(app, ["live"], input="new-football-key\n")
        assert "key" in result.output.lower()


class TestStandingsCommand:
    def test_exits_0_on_success(self, mock_client):
        result = runner.invoke(app, ["standings", "pl"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_client):
        mock_client.get_standings.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["standings", "pl"])
        assert result.exit_code == 1

    def test_exits_1_on_api_error(self, mock_client):
        mock_client.get_standings.side_effect = ApiError("competition not found", 404)
        result = runner.invoke(app, ["standings", "invalid"])
        assert result.exit_code == 1

    def test_exits_1_on_auth_error(self, mock_client):
        mock_client.get_standings.side_effect = AuthError("forbidden", 403)
        result = runner.invoke(app, ["standings", "pl"])
        assert result.exit_code == 1

    def test_shows_standings_data(self, mock_client):
        mock_client.get_standings.return_value = {
            "competition": {"name": "Premier League"},
            "standings": [
                {
                    "table": [
                        {
                            "position": 1,
                            "team": {"name": "Arsenal", "shortName": "Arsenal"},
                            "playedGames": 38, "won": 26, "draw": 6, "lost": 6,
                            "goalsFor": 88, "goalsAgainst": 43,
                            "goalDifference": 45, "points": 84,
                        }
                    ]
                }
            ],
        }
        result = runner.invoke(app, ["standings", "pl"])
        assert result.exit_code == 0
        assert "Arsenal" in result.output


class TestFixturesCommand:
    def test_exits_0_on_success(self, mock_client):
        result = runner.invoke(app, ["fixtures", "pl"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_client):
        mock_client.get_fixtures.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["fixtures", "pl"])
        assert result.exit_code == 1

    def test_exits_1_on_auth_error(self, mock_client):
        mock_client.get_fixtures.side_effect = AuthError("unauthorized", 401)
        result = runner.invoke(app, ["fixtures", "pl"])
        assert result.exit_code == 1

    def test_exits_1_on_api_error(self, mock_client):
        mock_client.get_fixtures.side_effect = ApiError("not found", 404)
        result = runner.invoke(app, ["fixtures", "xyz"])
        assert result.exit_code == 1
