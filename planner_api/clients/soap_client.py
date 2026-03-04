from zeep import Client
from zeep.transports import Transport
from requests import Session


class SoapTripTimeClient:
    def __init__(self, wsdl_url: str):
        session = Session()
        session.timeout = 10
        transport = Transport(session=session)
        self.client = Client(wsdl=wsdl_url, transport=transport)

    def estimate_trip_time(
        self,
        distance_km: float,
        autonomy_km: float,
        avg_speed_kmh: float,
        charge_time_min_per_stop: int
    ) -> dict:
        # Le nom exact est celui de la méthode Spyne: estimate_trip_time
        res = self.client.service.estimate_trip_time(
            distance_km,
            autonomy_km,
            avg_speed_kmh,
            charge_time_min_per_stop
        )

        # Zeep retourne un objet; on le convertit en dict simple
        return {
            "stops": int(res.stops),
            "drive_time_min": float(res.drive_time_min),
            "charge_time_min_total": float(res.charge_time_min_total),
            "total_time_min": float(res.total_time_min),
            "message": str(res.message),
        }