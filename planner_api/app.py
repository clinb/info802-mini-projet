from flask import Flask, jsonify, request
from config import SOAP_WSDL_URL, GRAPHQL_URL, NOMINATIM_URL, OSRM_URL, IRVE_BASE_URL, IRVE_DATASET, IRVE_RADIUS_M
from clients.soap_client import SoapTripTimeClient
from clients.graphql_client import GraphQLVehiclesClient
from clients.geocode_client import GeocoderClient
from clients.routing_client import OsrmRoutingClient
from clients.irve_client import IrveClient
import polyline as polyline_lib
from utils.geo_utils import pick_stop_points_along_polyline

app = Flask(__name__)

soap = SoapTripTimeClient(SOAP_WSDL_URL)
gql = GraphQLVehiclesClient(GRAPHQL_URL)
geocoder = GeocoderClient(NOMINATIM_URL)
router = OsrmRoutingClient(OSRM_URL)
irve = IrveClient(IRVE_BASE_URL, IRVE_DATASET)

RADIUS_FALLBACKS = [5_000, 10_000, 20_000, 50_000]

def find_nearest_charger_with_fallback(irve_client, lat: float, lon: float):
    for r in RADIUS_FALLBACKS:
        charger = irve_client.nearest_charger(lat=lat, lon=lon, radius_m=r)
        if charger is not None:
            charger["search_radius_m"] = r  # pratique pour debug
            return charger
    return None

@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/vehicles/<vehicle_id>")
def get_vehicle(vehicle_id: str):
    v = gql.get_vehicle_by_id(vehicle_id)
    if v is None:
        return jsonify({"error": "vehicle_not_found"}), 404
    return jsonify(v)


@app.post("/api/plan")
def plan_v1_distance():
    """
    V1 (déjà OK):
    { "distance_km": 436, "vehicle_id": "v1" }
    """
    body = request.get_json(silent=True) or {}
    vehicle_id = body.get("vehicle_id")
    distance_km = body.get("distance_km")

    if not vehicle_id or distance_km is None:
        return jsonify({"error": "missing_vehicle_id_or_distance_km"}), 400

    v = gql.get_vehicle_by_id(vehicle_id)
    if v is None:
        return jsonify({"error": "vehicle_not_found"}), 404

    time_res = soap.estimate_trip_time(
        distance_km=float(distance_km),
        autonomy_km=float(v["rangeKm"]),
        avg_speed_kmh=float(v["avgSpeedKmh"]),
        charge_time_min_per_stop=int(v["chargeTimeMin"]),
    )

    return jsonify({
        "input": {"distance_km": float(distance_km), "vehicle_id": vehicle_id},
        "vehicle": v,
        "time": time_res,
    })


@app.post("/api/plan-route")
def plan_v2_from_to():
    """
    V2:
    { "from": "Chambéry", "to": "Lyon", "vehicle_id": "v1" }
    """
    body = request.get_json(silent=True) or {}
    vehicle_id = body.get("vehicle_id")
    from_q = body.get("from")
    to_q = body.get("to")

    if not vehicle_id or not from_q or not to_q:
        return jsonify({"error": "missing_vehicle_id_or_from_or_to"}), 400

    v = gql.get_vehicle_by_id(vehicle_id)
    if v is None:
        return jsonify({"error": "vehicle_not_found"}), 404

    start = geocoder.geocode(from_q)
    end = geocoder.geocode(to_q)

    if start is None:
        return jsonify({"error": "from_not_found"}), 400
    if end is None:
        return jsonify({"error": "to_not_found"}), 400

    route = router.route(start["lat"], start["lon"], end["lat"], end["lon"])

    time_res = soap.estimate_trip_time(
        distance_km=float(route["distance_km"]),
        autonomy_km=float(v["rangeKm"]),
        avg_speed_kmh=float(v["avgSpeedKmh"]),
        charge_time_min_per_stop=int(v["chargeTimeMin"]),
    )

    decoded_points = polyline_lib.decode(route["polyline"]) 
    stop_points = pick_stop_points_along_polyline(decoded_points, time_res["stops"])

    chargers = []
    for (lat, lon) in stop_points:
        borne = find_nearest_charger_with_fallback(irve, lat, lon)

        chargers.append({
            "stop": {"lat": lat, "lon": lon},
            "charger": borne
        })

    return jsonify({
        "input": {
            "from": from_q,
            "to": to_q,
            "vehicle_id": vehicle_id,
            "start": start,
            "end": end,
        },
        "vehicle": v,
        "route": route,
        "time": time_res,
        "stop_points": [{"lat": lat, "lon": lon} for (lat, lon) in stop_points],
        "chargers": chargers,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)