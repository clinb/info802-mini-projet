import requests


class ServiceItineraireOpenStreet:
    def __init__(self, base_url: str, api_key: str, timeout_s: int = 20):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s

    def calculer_itineraire(self, depart_lat: float, depart_lng: float, arrivee_lat: float, arrivee_lng: float) -> dict:
        """
        Appelle l’API Open-street route.
        Retour attendu: au moins polyline + une distance (si dispo).
        """
        url = f"{self.base_url}/route/"
        params = {
            "origin": f"{depart_lat},{depart_lng}",
            "destination": f"{arrivee_lat},{arrivee_lng}",
            "mode": "driving",
            "key": self.api_key,
        }

        r = requests.get(url, params=params, timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()