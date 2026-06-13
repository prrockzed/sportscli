import pytest
from unittest.mock import patch
from typer.testing import CliRunner

from sportscli.cli import app
import sportscli.config as config_module

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))


class TestRootCommand:
    def test_exits_0_with_no_args(self):
        result = runner.invoke(app, [])
        assert result.exit_code == 0

    def test_welcome_output_contains_sportscli(self):
        result = runner.invoke(app, [])
        assert "sportscli" in result.output.lower()

    def test_help_lists_chess_subcommand(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "chess" in result.output

    def test_help_lists_cricket_subcommand(self):
        result = runner.invoke(app, ["--help"])
        assert "cricket" in result.output

    def test_help_lists_football_subcommand(self):
        result = runner.invoke(app, ["--help"])
        assert "football" in result.output

    def test_help_lists_config_subcommand(self):
        result = runner.invoke(app, ["--help"])
        assert "config" in result.output


class TestChessSubcommandRegistered:
    def test_chess_help_exits_0(self):
        result = runner.invoke(app, ["chess", "--help"])
        assert result.exit_code == 0

    def test_chess_help_lists_tournaments(self):
        result = runner.invoke(app, ["chess", "--help"])
        assert "tournaments" in result.output

    def test_chess_help_lists_live(self):
        result = runner.invoke(app, ["chess", "--help"])
        assert "live" in result.output

    def test_chess_help_lists_broadcasts(self):
        result = runner.invoke(app, ["chess", "--help"])
        assert "broadcasts" in result.output

    def test_chess_help_lists_player(self):
        result = runner.invoke(app, ["chess", "--help"])
        assert "player" in result.output


class TestCricketSubcommandRegistered:
    def test_cricket_help_exits_0(self):
        result = runner.invoke(app, ["cricket", "--help"])
        assert result.exit_code == 0

    def test_cricket_help_lists_live(self):
        result = runner.invoke(app, ["cricket", "--help"])
        assert "live" in result.output

    def test_cricket_help_lists_scorecard(self):
        result = runner.invoke(app, ["cricket", "--help"])
        assert "scorecard" in result.output

    def test_cricket_help_lists_schedule(self):
        result = runner.invoke(app, ["cricket", "--help"])
        assert "schedule" in result.output


class TestFootballSubcommandRegistered:
    def test_football_help_exits_0(self):
        result = runner.invoke(app, ["football", "--help"])
        assert result.exit_code == 0

    def test_football_help_lists_live(self):
        result = runner.invoke(app, ["football", "--help"])
        assert "live" in result.output

    def test_football_help_lists_standings(self):
        result = runner.invoke(app, ["football", "--help"])
        assert "standings" in result.output

    def test_football_help_lists_fixtures(self):
        result = runner.invoke(app, ["football", "--help"])
        assert "fixtures" in result.output


class TestConfigSet:
    def test_exits_0_on_success(self):
        result = runner.invoke(app, ["config", "set", "cricket", "my-key-abc"])
        assert result.exit_code == 0

    def test_key_is_persisted(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))
        runner.invoke(app, ["config", "set", "cricket", "persisted-key"])
        assert config_module.get_api_key("cricket") == "persisted-key"

    def test_football_key_is_persisted(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))
        runner.invoke(app, ["config", "set", "football", "fb-key-xyz"])
        assert config_module.get_api_key("football") == "fb-key-xyz"

    def test_unknown_sport_still_saves(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))
        runner.invoke(app, ["config", "set", "tennis", "tennis-key"])
        assert config_module.get_api_key("tennis") == "tennis-key"


class TestConfigShow:
    def test_exits_0_with_no_config(self):
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0

    def test_shows_message_when_no_keys_stored(self):
        result = runner.invoke(app, ["config", "show"])
        output_lower = result.output.lower()
        assert "no" in output_lower or "config" in output_lower

    def test_shows_masked_key_after_set(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))
        runner.invoke(app, ["config", "set", "cricket", "abcdef123456"])
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        # First 6 chars visible, rest masked
        assert "abcdef" in result.output
        # Full key must not be visible
        assert "abcdef123456" not in result.output

    def test_shows_sport_name_in_output(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))
        runner.invoke(app, ["config", "set", "football", "abcdef789"])
        result = runner.invoke(app, ["config", "show"])
        assert "football" in result.output
