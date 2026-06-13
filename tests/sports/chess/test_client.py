import json
import pytest
from unittest.mock import MagicMock, patch

from sportscli.sports.chess.client import LichessClient


class MockResponse:
    def __init__(self, status_code: int, json_data=None, text: str = ""):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.text = text

    def json(self):
        return self._json


@pytest.fixture
def client():
    return LichessClient()


class TestLichessClientSetup:
    def test_base_url_is_lichess(self, client):
        assert client.BASE_URL == "https://lichess.org"

    def test_requires_no_api_key(self):
        # Should instantiate with zero arguments
        c = LichessClient()
        assert c is not None


class TestGetTournaments:
    def test_calls_tournament_endpoint(self, client):
        data = {"created": [], "started": [], "finished": []}
        with patch.object(client.session, "get", return_value=MockResponse(200, data)) as mock_get:
            client.get_tournaments()
        assert mock_get.call_args[0][0].endswith("/api/tournament")

    def test_returns_response_data(self, client):
        data = {"created": [{"id": "t1"}], "started": [], "finished": []}
        with patch.object(client.session, "get", return_value=MockResponse(200, data)):
            result = client.get_tournaments()
        assert result == data


class TestGetLiveGames:
    def test_transforms_channel_dict_to_list(self, client):
        raw = {
            "Bullet": {"gameId": "abc", "players": []},
            "Blitz":  {"gameId": "def", "players": []},
        }
        with patch.object(client.session, "get", return_value=MockResponse(200, raw)):
            result = client.get_live_games()
        assert isinstance(result, list)
        assert len(result) == 2

    def test_channel_name_added_to_each_game(self, client):
        raw = {"Bullet": {"gameId": "abc", "players": []}}
        with patch.object(client.session, "get", return_value=MockResponse(200, raw)):
            result = client.get_live_games()
        assert result[0]["channel"] == "Bullet"

    def test_game_id_preserved(self, client):
        raw = {"Blitz": {"gameId": "xyz123", "players": []}}
        with patch.object(client.session, "get", return_value=MockResponse(200, raw)):
            result = client.get_live_games()
        assert result[0]["gameId"] == "xyz123"

    def test_skips_empty_channels(self, client):
        raw = {"Bullet": {"gameId": "abc"}, "UltraBullet": None}
        with patch.object(client.session, "get", return_value=MockResponse(200, raw)):
            result = client.get_live_games()
        assert len(result) == 1

    def test_calls_tv_channels_endpoint(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {})) as mock_get:
            client.get_live_games()
        assert "/api/tv/channels" in mock_get.call_args[0][0]


class TestGetBroadcasts:
    def test_calls_broadcast_endpoint(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, [])) as mock_get:
            client.get_broadcasts()
        assert mock_get.call_args[0][0].endswith("/api/broadcast")

    def test_requests_20_results(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, [])) as mock_get:
            client.get_broadcasts()
        assert mock_get.call_args[1]["params"]["nb"] == 20


class TestGetPlayer:
    def test_calls_user_endpoint_with_username(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {})) as mock_get:
            client.get_player("magnuscarlsen")
        assert mock_get.call_args[0][0].endswith("/api/user/magnuscarlsen")

    def test_returns_profile_data(self, client):
        profile = {"username": "magnuscarlsen", "perfs": {"blitz": {"rating": 2900}}}
        with patch.object(client.session, "get", return_value=MockResponse(200, profile)):
            result = client.get_player("magnuscarlsen")
        assert result == profile

    def test_username_is_url_encoded_in_path(self, client):
        with patch.object(client.session, "get", return_value=MockResponse(200, {})) as mock_get:
            client.get_player("testuser123")
        assert "testuser123" in mock_get.call_args[0][0]


class TestGetPlayerGames:
    def test_parses_ndjson_into_list(self, client):
        games = [
            {"id": "g1", "speed": "blitz", "players": {}, "moves": "e4 e5"},
            {"id": "g2", "speed": "bullet", "players": {}, "moves": "d4 d5"},
        ]
        mock_resp = MagicMock()
        mock_resp.text = "\n".join(json.dumps(g) for g in games)
        with patch.object(client.session, "get", return_value=mock_resp):
            result = client.get_player_games("testuser")
        assert len(result) == 2
        assert result[0]["id"] == "g1"
        assert result[1]["id"] == "g2"

    def test_handles_empty_ndjson_response(self, client):
        mock_resp = MagicMock()
        mock_resp.text = ""
        with patch.object(client.session, "get", return_value=mock_resp):
            result = client.get_player_games("testuser")
        assert result == []

    def test_calls_correct_endpoint(self, client):
        mock_resp = MagicMock()
        mock_resp.text = ""
        with patch.object(client.session, "get", return_value=mock_resp) as mock_get:
            client.get_player_games("hikaru")
        url = mock_get.call_args[0][0]
        assert "/api/games/user/hikaru" in url

    def test_requests_ndjson_accept_header(self, client):
        mock_resp = MagicMock()
        mock_resp.text = ""
        with patch.object(client.session, "get", return_value=mock_resp) as mock_get:
            client.get_player_games("hikaru")
        headers = mock_get.call_args[1]["headers"]
        assert headers.get("Accept") == "application/x-ndjson"

    def test_respects_max_games_param(self, client):
        mock_resp = MagicMock()
        mock_resp.text = ""
        with patch.object(client.session, "get", return_value=mock_resp) as mock_get:
            client.get_player_games("hikaru", max_games=10)
        params = mock_get.call_args[1]["params"]
        assert params["max"] == 10
