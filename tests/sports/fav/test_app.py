import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from sportscli.core.exceptions import ApiError, AuthError, NetworkError
from sportscli.sports.fav.app import app

runner = CliRunner()

_DRIVER_STANDINGS_DATA = {
    "MRData": {
        "StandingsTable": {
            "StandingsLists": [{
                "season": "2025",
                "round": "10",
                "DriverStandings": [
                    {
                        "position": "1",
                        "points": "291",
                        "wins": "9",
                        "Driver": {
                            "driverId": "verstappen",
                            "givenName": "Max",
                            "familyName": "Verstappen",
                            "nationality": "Dutch",
                        },
                        "Constructors": [{"name": "Red Bull Racing"}],
                    },
                    {
                        "position": "2",
                        "points": "180",
                        "wins": "2",
                        "Driver": {
                            "driverId": "hamilton",
                            "givenName": "Lewis",
                            "familyName": "Hamilton",
                            "nationality": "British",
                        },
                        "Constructors": [{"name": "Mercedes"}],
                    },
                ],
            }]
        }
    }
}

_CONSTRUCTOR_STANDINGS_DATA = {
    "MRData": {
        "StandingsTable": {
            "StandingsLists": [{
                "season": "2025",
                "round": "10",
                "ConstructorStandings": [
                    {
                        "position": "1",
                        "points": "450",
                        "wins": "10",
                        "Constructor": {
                            "constructorId": "red_bull",
                            "name": "Red Bull Racing",
                            "nationality": "Austrian",
                        },
                    },
                    {
                        "position": "2",
                        "points": "320",
                        "wins": "3",
                        "Constructor": {
                            "constructorId": "ferrari",
                            "name": "Ferrari",
                            "nationality": "Italian",
                        },
                    },
                ],
            }]
        }
    }
}

_FOOTBALL_STANDINGS_DATA = {
    "competition": {"name": "Premier League"},
    "standings": [
        {
            "table": [
                {
                    "position": 1,
                    "team": {"name": "Arsenal"},
                    "playedGames": 38, "won": 26, "draw": 6, "lost": 6,
                    "goalDifference": 45, "points": 84,
                }
            ]
        }
    ],
}

_CHESS_PROFILE = {
    "id": "magnuscarlsen",
    "username": "magnuscarlsen",
    "perfs": {
        "blitz":     {"rating": 3208},
        "rapid":     {"rating": 2876},
        "classical": {"rating": 2850},
        "bullet":    {"rating": 3350},
    },
}


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------

class TestAddCommand:
    def test_exits_0_on_valid_category(self):
        result = runner.invoke(app, ["add", "chess", "magnuscarlsen"])
        assert result.exit_code == 0

    def test_success_message_shown(self):
        result = runner.invoke(app, ["add", "chess", "magnuscarlsen"])
        assert "magnuscarlsen" in result.output

    def test_exits_1_on_unknown_category(self):
        result = runner.invoke(app, ["add", "basketball", "lebron"])
        assert result.exit_code == 1

    def test_unknown_category_shows_warning(self):
        result = runner.invoke(app, ["add", "basketball", "lebron"])
        assert "Unknown category" in result.output

    def test_f1_driver_category_accepted(self):
        result = runner.invoke(app, ["add", "f1-driver", "verstappen"])
        assert result.exit_code == 0

    def test_f1_constructor_category_accepted(self):
        result = runner.invoke(app, ["add", "f1-constructor", "red_bull"])
        assert result.exit_code == 0

    def test_football_category_accepted(self):
        result = runner.invoke(app, ["add", "football", "pl"])
        assert result.exit_code == 0

    def test_value_stored_in_config(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))
        runner.invoke(app, ["add", "chess", "hikaru"])
        import sportscli.config as cfg
        favs = cfg.get_favourites()
        assert "hikaru" in favs.get("chess", [])

    def test_duplicate_not_added_twice(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))
        runner.invoke(app, ["add", "chess", "hikaru"])
        runner.invoke(app, ["add", "chess", "hikaru"])
        import sportscli.config as cfg
        favs = cfg.get_favourites()
        assert favs.get("chess", []).count("hikaru") == 1

    def test_value_stored_as_lowercase(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))
        runner.invoke(app, ["add", "chess", "MagnusCarlsen"])
        import sportscli.config as cfg
        favs = cfg.get_favourites()
        assert "magnuscarlsen" in favs.get("chess", [])


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------

class TestRemoveCommand:
    def _add(self, category, value):
        runner.invoke(app, ["add", category, value])

    def test_exits_0_when_item_exists(self):
        self._add("chess", "hikaru")
        result = runner.invoke(app, ["remove", "chess", "hikaru"])
        assert result.exit_code == 0

    def test_success_message_on_removal(self):
        self._add("chess", "hikaru")
        result = runner.invoke(app, ["remove", "chess", "hikaru"])
        assert "hikaru" in result.output

    def test_warning_when_item_not_present(self):
        result = runner.invoke(app, ["remove", "chess", "nobody"])
        assert "not in" in result.output.lower() or "warning" in result.output.lower()

    def test_exits_1_on_unknown_category(self):
        result = runner.invoke(app, ["remove", "basketball", "lebron"])
        assert result.exit_code == 1

    def test_item_removed_from_config(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SPORTSCLI_CONFIG_DIR", str(tmp_path))
        runner.invoke(app, ["add", "chess", "hikaru"])
        runner.invoke(app, ["remove", "chess", "hikaru"])
        import sportscli.config as cfg
        favs = cfg.get_favourites()
        assert "hikaru" not in favs.get("chess", [])


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

class TestListCommand:
    def test_exits_0_when_no_favourites(self):
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0

    def test_shows_empty_message_when_no_favourites(self):
        result = runner.invoke(app, ["list"])
        assert "No favourites" in result.output

    def test_shows_saved_chess_player(self):
        runner.invoke(app, ["add", "chess", "magnuscarlsen"])
        result = runner.invoke(app, ["list"])
        assert "magnuscarlsen" in result.output

    def test_shows_saved_f1_driver(self):
        runner.invoke(app, ["add", "f1-driver", "verstappen"])
        result = runner.invoke(app, ["list"])
        assert "verstappen" in result.output

    def test_shows_saved_football_league(self):
        runner.invoke(app, ["add", "football", "pl"])
        result = runner.invoke(app, ["list"])
        assert "pl" in result.output

    def test_shows_multiple_items(self):
        runner.invoke(app, ["add", "chess", "hikaru"])
        runner.invoke(app, ["add", "chess", "magnuscarlsen"])
        result = runner.invoke(app, ["list"])
        assert "hikaru" in result.output
        assert "magnuscarlsen" in result.output


# ---------------------------------------------------------------------------
# show — chess
# ---------------------------------------------------------------------------

class TestShowCommandChess:
    def test_exits_0_with_chess_favourite(self):
        runner.invoke(app, ["add", "chess", "magnuscarlsen"])
        with patch("sportscli.sports.fav.app.LichessClient") as MockClient:
            MockClient.return_value.get_player.return_value = _CHESS_PROFILE
            result = runner.invoke(app, ["show"])
        assert result.exit_code == 0

    def test_shows_chess_rating(self):
        runner.invoke(app, ["add", "chess", "magnuscarlsen"])
        with patch("sportscli.sports.fav.app.LichessClient") as MockClient:
            MockClient.return_value.get_player.return_value = _CHESS_PROFILE
            result = runner.invoke(app, ["show"])
        assert "3208" in result.output

    def test_chess_network_error_prints_error(self):
        runner.invoke(app, ["add", "chess", "magnuscarlsen"])
        with patch("sportscli.sports.fav.app.LichessClient") as MockClient:
            MockClient.return_value.get_player.side_effect = NetworkError("timeout")
            result = runner.invoke(app, ["show"])
        assert "Network error" in result.output

    def test_chess_api_error_prints_error(self):
        runner.invoke(app, ["add", "chess", "unknown_user"])
        with patch("sportscli.sports.fav.app.LichessClient") as MockClient:
            MockClient.return_value.get_player.side_effect = ApiError("not found", 404)
            result = runner.invoke(app, ["show"])
        assert "error" in result.output.lower()


# ---------------------------------------------------------------------------
# show — F1
# ---------------------------------------------------------------------------

class TestShowCommandF1:
    def test_shows_f1_driver(self):
        runner.invoke(app, ["add", "f1-driver", "verstappen"])
        with patch("sportscli.sports.fav.app.F1Client") as MockF1:
            MockF1.return_value.get_driver_standings.return_value = _DRIVER_STANDINGS_DATA
            result = runner.invoke(app, ["show"])
        assert "Verstappen" in result.output

    def test_f1_driver_not_in_standings_shows_not_found(self):
        runner.invoke(app, ["add", "f1-driver", "nobody"])
        with patch("sportscli.sports.fav.app.F1Client") as MockF1:
            MockF1.return_value.get_driver_standings.return_value = _DRIVER_STANDINGS_DATA
            result = runner.invoke(app, ["show"])
        assert result.exit_code == 0

    def test_f1_driver_network_error(self):
        runner.invoke(app, ["add", "f1-driver", "verstappen"])
        with patch("sportscli.sports.fav.app.F1Client") as MockF1:
            MockF1.return_value.get_driver_standings.side_effect = NetworkError("timeout")
            result = runner.invoke(app, ["show"])
        assert "error" in result.output.lower()

    def test_shows_f1_constructor(self):
        runner.invoke(app, ["add", "f1-constructor", "red_bull"])
        with patch("sportscli.sports.fav.app.F1Client") as MockF1:
            MockF1.return_value.get_constructor_standings.return_value = _CONSTRUCTOR_STANDINGS_DATA
            result = runner.invoke(app, ["show"])
        assert "Red Bull Racing" in result.output

    def test_f1_constructor_network_error(self):
        runner.invoke(app, ["add", "f1-constructor", "red_bull"])
        with patch("sportscli.sports.fav.app.F1Client") as MockF1:
            MockF1.return_value.get_constructor_standings.side_effect = NetworkError("timeout")
            result = runner.invoke(app, ["show"])
        assert "error" in result.output.lower()


# ---------------------------------------------------------------------------
# show — football
# ---------------------------------------------------------------------------

class TestShowCommandFootball:
    def test_shows_league_when_key_present(self):
        runner.invoke(app, ["add", "football", "pl"])
        with patch("sportscli.sports.fav.app.config.get_api_key", return_value="test-key"):
            with patch("sportscli.sports.fav.app.FootballDataClient") as MockFB:
                MockFB.return_value.get_standings.return_value = _FOOTBALL_STANDINGS_DATA
                result = runner.invoke(app, ["show"])
        assert "Arsenal" in result.output

    def test_warns_when_no_football_key(self):
        runner.invoke(app, ["add", "football", "pl"])
        with patch("sportscli.sports.fav.app.config.get_api_key", return_value=None):
            result = runner.invoke(app, ["show"])
        assert "football api key" in result.output.lower()

    def test_football_network_error(self):
        runner.invoke(app, ["add", "football", "pl"])
        with patch("sportscli.sports.fav.app.config.get_api_key", return_value="test-key"):
            with patch("sportscli.sports.fav.app.FootballDataClient") as MockFB:
                MockFB.return_value.get_standings.side_effect = NetworkError("timeout")
                result = runner.invoke(app, ["show"])
        assert "error" in result.output.lower()

    def test_football_auth_error_stops_further_requests(self):
        runner.invoke(app, ["add", "football", "pl"])
        runner.invoke(app, ["add", "football", "ucl"])
        with patch("sportscli.sports.fav.app.config.get_api_key", return_value="bad-key"):
            with patch("sportscli.sports.fav.app.FootballDataClient") as MockFB:
                MockFB.return_value.get_standings.side_effect = AuthError("forbidden", 403)
                result = runner.invoke(app, ["show"])
        assert "API key" in result.output


# ---------------------------------------------------------------------------
# show — empty favourites
# ---------------------------------------------------------------------------

class TestShowCommandEmpty:
    def test_exits_0_when_no_favourites(self):
        result = runner.invoke(app, ["show"])
        assert result.exit_code == 0

    def test_warns_when_no_favourites(self):
        result = runner.invoke(app, ["show"])
        assert "No favourites" in result.output
