from sportscli.core.http import BaseAPIClient


class F1Client(BaseAPIClient):
    """Jolpica F1 API client — season schedule, standings, race results."""

    BASE_URL = "https://api.jolpi.ca/ergast/f1"

    def get_schedule(self, season: str = "current") -> dict:
        return self.get(f"/{season}/races.json")

    def get_driver_standings(self, season: str = "current") -> dict:
        return self.get(f"/{season}/driverStandings.json")

    def get_constructor_standings(self, season: str = "current") -> dict:
        return self.get(f"/{season}/constructorStandings.json")

    def get_race_results(self, season: str = "current", round: str = "last") -> dict:
        return self.get(f"/{season}/{round}/results.json")


class OpenF1Client(BaseAPIClient):
    """OpenF1 API client — real-time session and position data."""

    BASE_URL = "https://api.openf1.org/v1"

    def get_latest_session(self) -> list:
        return self.get("/sessions", params={"session_key": "latest"})

    def get_positions(self, session_key: int) -> list:
        return self.get("/position", params={"session_key": session_key})

    def get_drivers(self, session_key: int) -> list:
        return self.get("/drivers", params={"session_key": session_key})
