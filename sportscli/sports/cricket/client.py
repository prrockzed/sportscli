from sportscli.core.http import BaseAPIClient


class CricketDataClient(BaseAPIClient):
    BASE_URL = "https://api.cricapi.com/v1"

    def __init__(self, api_key: str):
        super().__init__()
        self._api_key = api_key

    def _params(self, extra: dict | None = None) -> dict:
        params = {"apikey": self._api_key, "offset": 0}
        if extra:
            params.update(extra)
        return params

    def get_live_matches(self) -> dict:
        return self.get("/currentMatches", params=self._params())

    def get_scorecard(self, match_id: str) -> dict:
        return self.get("/match_scorecard", params=self._params({"id": match_id}))

    def get_schedule(self) -> dict:
        return self.get("/matches", params=self._params())
