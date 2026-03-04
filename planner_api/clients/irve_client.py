import requests


class IrveClient:
    def __init__(self, base_url: str, dataset: str):
        self.base_url = base_url
        self.dataset = dataset

    def nearest_charger(self, lat: float, lon: float, radius_m: int = 5000) -> dict | None:
        """
        IMPORTANT (dataset bornes-irve ODRÉ):
        - geofilter.distance attend lon,lat,radius
        - geometry.coordinates est incohérent -> on privilégie consolidated_latitude/longitude
        """
        params = {
            "dataset": self.dataset,
            "rows": 1,
            "geofilter.distance": f"{lon},{lat},{radius_m}",  # <-- lon,lat
            "sort": "dist",
        }
        headers = {"User-Agent": "info802-tp-ve/1.0 (student-project)"}
        r = requests.get(self.base_url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        payload = r.json()

        records = payload.get("records") or []
        if not records:
            return None

        rec = records[0]
        fields = rec.get("fields") or {}

        # On reconstruit une "position" fiable depuis les champs consolidés
        lat2 = fields.get("consolidated_latitude")
        lon2 = fields.get("consolidated_longitude")

        pos = None
        try:
            if lat2 is not None and lon2 is not None:
                pos = {"lat": float(lat2), "lon": float(lon2)}
        except Exception:
            pos = None

        return {
            "recordid": rec.get("recordid"),
            "datasetid": rec.get("datasetid"),
            "dist_m": float(fields.get("dist")) if fields.get("dist") is not None else None,
            "position": pos,
            # Champs utiles (tu peux en ajouter)
            "name": fields.get("nom_station"),
            "operator": fields.get("nom_operateur"),
            "address": fields.get("adresse_station"),
            "power_kw": fields.get("puissance_nominale"),
            "pdc_count": fields.get("nbre_pdc"),
            "payment_cb": fields.get("paiement_cb"),
            "fields": fields,
        }