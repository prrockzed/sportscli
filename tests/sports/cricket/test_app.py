import pytest
from unittest.mock import patch
from typer.testing import CliRunner

from sportscli.core.exceptions import ApiError, AuthError, NetworkError
from sportscli.sports.cricket.app import app

runner = CliRunner()

_STORED_KEY = "stored-cricket-key"


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))


@pytest.fixture
def with_key():
    """Pre-supply an API key so commands skip the prompt."""
    with patch("sportscli.sports.cricket.app.config.get_api_key", return_value=_STORED_KEY):
        yield


@pytest.fixture
def mock_client(with_key):
    with patch("sportscli.sports.cricket.app.CricketDataClient") as MockClient:
        instance = MockClient.return_value
        instance.get_live_matches.return_value = {"data": []}
        instance.get_scorecard.return_value = {"data": {}}
        instance.get_schedule.return_value = {"data": []}
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
        mock_client.get_live_matches.side_effect = NetworkError("connection refused")
        result = runner.invoke(app, ["live"])
        assert "Network error" in result.output

    def test_exits_1_on_auth_error(self, mock_client):
        mock_client.get_live_matches.side_effect = AuthError("forbidden", 403)
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 1

    def test_auth_error_suggests_config_set(self, mock_client):
        mock_client.get_live_matches.side_effect = AuthError("unauthorized", 401)
        result = runner.invoke(app, ["live"])
        assert "config set cricket" in result.output

    def test_exits_1_on_api_error(self, mock_client):
        mock_client.get_live_matches.side_effect = ApiError("server error", 500)
        result = runner.invoke(app, ["live"])
        assert result.exit_code == 1

    def test_prompts_for_key_when_none_stored(self):
        with patch("sportscli.sports.cricket.app.config.get_api_key", return_value=None):
            with patch("sportscli.sports.cricket.app.CricketDataClient") as MockClient:
                MockClient.return_value.get_live_matches.return_value = {"data": []}
                result = runner.invoke(app, ["live"], input="new-api-key\n")
        assert "key" in result.output.lower()

    def test_key_saved_after_prompt(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))
        with patch("sportscli.sports.cricket.app.config.get_api_key", return_value=None):
            with patch("sportscli.sports.cricket.app.CricketDataClient") as MockClient:
                MockClient.return_value.get_live_matches.return_value = {"data": []}
                with patch("sportscli.sports.cricket.app.config.set_api_key") as mock_set:
                    runner.invoke(app, ["live"], input="saved-key\n")
                mock_set.assert_called_once_with("cricket", "saved-key")


class TestScorecardCommand:
    def test_exits_0_on_success(self, mock_client):
        result = runner.invoke(app, ["scorecard", "match-id-123"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_client):
        mock_client.get_scorecard.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["scorecard", "match-id-123"])
        assert result.exit_code == 1

    def test_exits_1_on_api_error(self, mock_client):
        mock_client.get_scorecard.side_effect = ApiError("not found", 404)
        result = runner.invoke(app, ["scorecard", "bad-id"])
        assert result.exit_code == 1

    def test_exits_1_on_auth_error(self, mock_client):
        mock_client.get_scorecard.side_effect = AuthError("unauthorized", 401)
        result = runner.invoke(app, ["scorecard", "match-id"])
        assert result.exit_code == 1


class TestScheduleCommand:
    def test_exits_0_on_success(self, mock_client):
        result = runner.invoke(app, ["schedule"])
        assert result.exit_code == 0

    def test_exits_1_on_network_error(self, mock_client):
        mock_client.get_schedule.side_effect = NetworkError("timeout")
        result = runner.invoke(app, ["schedule"])
        assert result.exit_code == 1

    def test_exits_1_on_api_error(self, mock_client):
        mock_client.get_schedule.side_effect = ApiError("internal error", 500)
        result = runner.invoke(app, ["schedule"])
        assert result.exit_code == 1
