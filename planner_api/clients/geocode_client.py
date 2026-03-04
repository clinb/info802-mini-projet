import requests


class GeocoderClient:
    def __init__(self, nominatim_url: str):
        self.url = nominatim_url

    def geocode(self, query: str) -> dict | None:
        """
        Retourne: {"lat": float, "lon": float, "display_name": str}
        """
        params = {
            "q": query,
            "format": "json",
            "limit": 1,
        }
        headers = {
            # Nominatim demande un User-Agent explicite
            "User-Agent": "info802-tp-ve/1.0 (student-project)"
        }
        r = requests.get(self.url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        d = data[0]
        return {
            "lat": float(d["lat"]),
            "lon": float(d["lon"]),
            "display_name": d.get("display_name", query),
        }