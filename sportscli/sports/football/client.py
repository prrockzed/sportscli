from sportscli.core.http import BaseAPIClient

# League code → competition ID mapping for football-data.org
LEAGUE_IDS: dict[str, str] = {
    "pl": "PL",       # Premier League
    "bl1": "BL1",     # Bundesliga
    "sa": "SA",       # Serie A
    "pd": "PD",       # La Liga
    "fl1": "FL1",     # Ligue 1
    "ucl": "CL",      # UEFA Champions League
    "ec": "EC",       # European Championship
    "wc": "WC",       # FIFA World Cup
}


class FootballDataClient(BaseAPIClient):
    BASE_URL = "https://api.football-data.org/v4"

    def __init__(self, api_key: str):
        super().__init__()
        self.session.headers.update({"X-Auth-Token": api_key})

    def get_live_matches(self) -> dict:
        return self.get("/matches", params={"status": "LIVE"})

    def get_standings(self, league_code: str) -> dict:
        competition = LEAGUE_IDS.get(league_code.lower(), league_code.upper())
        return self.get(f"/competitions/{competition}/standings")

    def get_fixtures(self, league_code: str) -> dict:
        competition = LEAGUE_IDS.get(league_code.lower(), league_code.upper())
        return self.get(f"/competitions/{competition}/matches", params={"status": "SCHEDULED"})
