import requests
import polyline as polyline_lib


class OsrmRoutingClient:
    def __init__(self, osrm_base_url: str):
        self.base = osrm_base_url.rstrip("/")

    def route(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> dict:
        """
        OSRM attend: lon,lat;lon,lat
        Retourne: distance_km, duration_min, polyline, bbox, etc.
        """
        coords = f"{start_lon},{start_lat};{end_lon},{end_lat}"
        url = f"{self.base}/{coords}"

        params = {
            "overview": "full",
            "geometries": "polyline",
        }

        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        payload = r.json()

        if payload.get("code") != "Ok" or not payload.get("routes"):
            raise RuntimeError(f"OSRM error: {payload}")

        route = payload["routes"][0]
        distance_km = float(route["distance"]) / 1000.0
        duration_min = float(route["duration"]) / 60.0
        geom = route["geometry"]  # polyline encodée

        # On décode juste pour vérifier; utile plus tard pour calculer des points d'arrêts
        decoded_points = polyline_lib.decode(geom)  # [(lat, lon), ...]

        return {
            "distance_km": distance_km,
            "duration_min": duration_min,
            "polyline": geom,
            "points_count": len(decoded_points),
        }