from sportscli.core.http import BaseAPIClient


class LichessClient(BaseAPIClient):
    BASE_URL = "https://lichess.org"

    def get_tournaments(self) -> dict:
        return self.get("/api/tournament")

    def get_live_games(self) -> list[dict]:
        """Return current TV games grouped by time control."""
        data = self.get("/api/tv/channels")
        games = []
        for channel, info in data.items():
            if info:
                games.append({"channel": channel, **info})
        return games

    def get_broadcasts(self) -> dict:
        return self.get("/api/broadcast", params={"nb": 20})

    def get_player(self, username: str) -> dict:
        return self.get(f"/api/user/{username}")

    def get_player_games(self, username: str, max_games: int = 5) -> list[dict]:
        """Fetch recent rated games for a player (ndjson → list)."""
        import requests

        url = f"{self.BASE_URL}/api/games/user/{username}"
        params = {"max": max_games, "rated": "true", "pgnInJson": "false", "clocks": "false", "evals": "false"}
        response = self.session.get(url, params=params, timeout=self.TIMEOUT, headers={"Accept": "application/x-ndjson"})
        games = []
        for line in response.text.strip().splitlines():
            if line:
                import json
                games.append(json.loads(line))
        return games
