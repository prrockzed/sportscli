import pytest
from unittest.mock import patch
from typer.testing import CliRunner

from sportscli.core.exceptions import ApiError, AuthError, NetworkError, RateLimitError
from sportscli.sports.chess.app import app

runner = CliRunner()

_EMPTY_TOURNAMENTS = {"created": [], "started": [], "finished": []}
_EMPTY_PROFILE = {"username": "testuser", "perfs": {}}


@pytest.fixture
def mock_client():
    """Patch LichessClient in the chess app module for every test that uses it."""
    with patch("sportscli.sports.chess.app.LichessClient") as MockClient:
        instance = MockClient.return_value
        instance.get_tournaments.return_value = _EMPTY_TOURNAMENTS
        instance.get_live_games.return_value = []
        instance.get_broadcasts.return_value = []
        instance.get_player.return_value = _EMPTY_PROFILE
        instance.get_player_games.return_value = []
        yield instance


class TestTournamentsCommand:
    def test_exits_0_on_success(self, mock_client):
        result = runner.invoke(app, ["tournaments"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_client):
        mock_client.get_tournaments.side_effect = NetworkError("connection refused")
        result = runner.invoke(app, ["tournaments"])
        assert result.exit_code == 1

    def test_shows_network_error_in_output(self, mock_client):
        mock_client.get_tournaments.side_effect = NetworkError("DNS failure")
        result = runner.invoke(app, ["tournaments"])
        assert "Network error" in result.output

    def test_exits_1_on_api_error(self, mock_client):
        mock_client.get_tournaments.side_effect = ApiError("server error", 500)
        result = runner.invoke(app, ["tournaments"])
        assert result.exit_code == 1

    def test_shows_api_error_in_output(self, mock_client):
        mock_client.get_tournaments.side_effect = ApiError("bad gateway", 502)
        result = runner.invoke(app, ["tournaments"])
        assert "API error" in result.output

    def test_shows_live_tournaments_when_present(self, mock_client):
        mock_client.get_tournaments.return_value = {
            "started": [
                {
                    "fullName": "Bullet Arena",
                    "clock": {"limit": 60, "increment": 0},
                    "variant": {"name": "Standard"},
                    "nbPlayers": 200,
                }
            ],
            "created": [],
            "finished": [],
        }
        result = runner.invoke(app, ["tournaments"])
        assert result.exit_code == 0
        assert "Bullet Arena" in result.output


class TestLiveCommand:
    def test_exits_0_on_success(self, mock_client):
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_client):
        mock_client.get_live_games.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 1

    def test_exits_1_on_rate_limit_error(self, mock_client):
        mock_client.get_live_games.side_effect = RateLimitError("too many requests", 429)
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 1


class TestBroadcastsCommand:
    def test_exits_0_on_success(self, mock_client):
        result = runner.invoke(app, ["broadcasts"])
        assert result.exit_code == 0

    def test_exits_1_on_api_error(self, mock_client):
        mock_client.get_broadcasts.side_effect = ApiError("error", 500)
        result = runner.invoke(app, ["broadcasts"])
        assert result.exit_code == 1

    def test_exits_1_on_network_error(self, mock_client):
        mock_client.get_broadcasts.side_effect = NetworkError("no route")
        result = runner.invoke(app, ["broadcasts"])
        assert result.exit_code == 1


class TestPlayerCommand:
    def test_exits_0_on_success(self, mock_client):
        result = runner.invoke(app, ["player", "magnuscarlsen"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_client):
        mock_client.get_player.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["player", "magnuscarlsen"])
        assert result.exit_code == 1

    def test_exits_1_on_api_error(self, mock_client):
        mock_client.get_player.side_effect = ApiError("not found", 404)
        result = runner.invoke(app, ["player", "unknownuser"])
        assert result.exit_code == 1

    def test_shows_player_name_in_output(self, mock_client):
        mock_client.get_player.return_value = {
            "username": "hikaru",
            "perfs": {"blitz": {"rating": 2850, "games": 1000}},
        }
        result = runner.invoke(app, ["player", "hikaru"])
        assert result.exit_code == 0
        assert "hikaru" in result.output
