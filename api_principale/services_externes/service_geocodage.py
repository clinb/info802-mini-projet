import requests


class ServiceGeocodageOpenStreet:
    def __init__(self, base_url: str, api_key: str, timeout_s: int = 15):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s

    def geocoder_ville(self, ville: str) -> tuple[float, float]:
        """
        Retourne (lat, lng) pour une ville/adresse via l’API Open-street geocoding.
        """
        url = f"{self.base_url}/geocoding/"
        params = {
            "address": ville,
            "sensor": "false",
            "key": self.api_key,
        }

        r = requests.get(url, params=params, timeout=self.timeout_s)
        r.raise_for_status()
        data = r.json()

        results = data.get("results", [])
        if not results:
            raise ValueError(f"Aucun résultat de géocodage pour: {ville}")

        loc = results[0]["geometry"]["location"]
        return float(loc["lat"]), float(loc["lng"])