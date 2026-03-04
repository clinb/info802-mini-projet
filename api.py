from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import math
import requests

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict

# Import SOAP service directly (no HTTP calls needed)
from soap_triptime.app import TripTimeService


router = APIRouter(prefix="/api", tags=["api"])

# -------------------------
# Données véhicules (exemple)
# -------------------------
VEHICLES: Dict[str, Dict[str, Any]] = {
    "v1": {"id": "v1", "brand": "Tesla", "model": "Model 3", "rangeKm": 450, "avgSpeedKmh": 110, "chargeTimeMin": 25},
    "v2": {"id": "v2", "brand": "Renault", "model": "Mégane E-Tech", "rangeKm": 380, "avgSpeedKmh": 105, "chargeTimeMin": 30},
    "v3": {"id": "v3", "brand": "Peugeot", "model": "e-208", "rangeKm": 280, "avgSpeedKmh": 100, "chargeTimeMin": 35},
}

# Sample enriched vehicle list (simplified from Chargetrip sample)
VEHICLE_LIST: List[Dict[str, Any]] = [
    {
        "id": "5f043d91bc262f1627fc032f",
        "naming": {
            "make": "Audi",
            "model": "e-tron",
            "version": "55 quattro",
            "edition": None,
            "chargetrip_version": "55 quattro (2019 - 2020)"
        },
        "drivetrain": {"type": "BEV"},
        "connectors": [
            {"standard": "IEC_62196_T2", "power": 11, "max_electric_power": 11, "time": 555, "speed": 39},
            {"standard": "IEC_62196_T2_COMBO", "power": 147, "max_electric_power": 155, "time": 26, "speed": 590},
        ],
        "adapters": [],
        "battery": {"usable_kwh": 86.5, "full_kwh": 95},
        "body": {"seats": 5},
        "availability": {"status": "no_longer_available"},
        "range": {"chargetrip_range": {"best": 408, "worst": 364}},
        "media": {
            "image": {
                "id": "637cfd94fff76be0b355b82c",
                "type": "image",
                "url": "https://cars.chargetrip.io/637cfd94fff76be0b355b82c.png",
                "height": 400,
                "width": 697,
                "thumbnail_url": "https://cars.chargetrip.io/637cfd94fff76be0b355b82c-eb92fb5e6c7433d5e31dbe682f7ae922e78a232c.png",
                "thumbnail_height": 150,
                "thumbnail_width": 262,
            },
            "brand": {
                "id": "644924f42c8dee1ba0e11c3a",
                "type": "brand",
                "url": "https://cars.chargetrip.io/5f1aa826657beb21bf6388c0.png",
                "height": 432,
                "width": 768,
                "thumbnail_url": "https://cars.chargetrip.io/5f1aa826657beb21bf6388c0-8dcb18ef1be43017f302d60294cea469e26e66bc.png",
                "thumbnail_height": 24,
                "thumbnail_width": 56,
            },
            "video": {"id": None, "url": None},
        },
        "routing": {"fast_charging_support": True},
        "connect": {"providers": ["Enode"]},
    },
    {
        "id": "5d161beec9eef4c250d9d225",
        "naming": {"make": "BMW", "model": "i3s", "version": "94 Ah", "edition": None, "chargetrip_version": "94 Ah (2017 - 2018)"},
        "drivetrain": {"type": "BEV"},
        "connectors": [
            {"standard": "IEC_62196_T2", "power": 7.4, "max_electric_power": 7.4, "time": 270, "speed": 36},
            {"standard": "IEC_62196_T2_COMBO", "power": 46, "max_electric_power": 49, "time": 26, "speed": 250},
        ],
        "adapters": [],
        "battery": {"usable_kwh": 27.2, "full_kwh": 33.2},
        "body": {"seats": 4},
        "availability": {"status": "no_longer_available"},
        "range": {"chargetrip_range": {"best": 178, "worst": 157}},
        "media": {
            "image": {"id": "642d1eda4cf97628eaa7b417", "type": "image", "url": "https://cars.chargetrip.io/642d1eda4cf97628eaa7b417.png", "height": 864, "width": 1536, "thumbnail_url": "https://cars.chargetrip.io/642d1eda4cf97628eaa7b417-40d894fa72aaf7156e5ba45dcdc06134328da533.png", "thumbnail_height": 144, "thumbnail_width": 262},
            "brand": {"id": "654ce2585e76cf4d02fcbf92", "type": "brand", "url": "https://cars.chargetrip.io/654ce2585e76cf4d02fcbf92.png", "height": 432, "width": 768, "thumbnail_url": "https://cars.chargetrip.io/654ce2585e76cf4d02fcbf92-66d8c3f4bbe29c13a2f311ed944c4d2c319efa28.png", "thumbnail_height": 48, "thumbnail_width": 112},
            "video": {"id": None, "url": None},
        },
        "routing": {"fast_charging_support": True},
        "connect": {"providers": ["Enode"]},
    },
    {
        "id": "5f98238a7473fe6a4cbb813f",
        "naming": {"make": "Tesla", "model": "Model 3", "version": "Performance", "edition": None, "chargetrip_version": "Long Range Performance (2020 -  2022)"},
        "drivetrain": {"type": "BEV"},
        "connectors": [
            {"standard": "IEC_62196_T2", "power": 11, "max_electric_power": 11, "time": 495, "speed": 57},
            {"standard": "TESLA_S", "power": 135, "max_electric_power": 250, "time": 25, "speed": 790},
            {"standard": "IEC_62196_T2_COMBO", "power": 135, "max_electric_power": 250, "time": 25, "speed": 790},
        ],
        "adapters": [],
        "battery": {"usable_kwh": 76, "full_kwh": 82},
        "body": {"seats": 5},
        "availability": {"status": "no_longer_available"},
        "range": {"chargetrip_range": {"best": 497, "worst": 440}},
        "media": {"image": {"id": "5fa3ff3c8de02aab81e8443e", "type": "image", "url": "https://cars.chargetrip.io/5fa3ff3c8de02aab81e8443e.png", "height": 864, "width": 1536, "thumbnail_url": "https://cars.chargetrip.io/5fa3ff3c8de02aab81e8443e-0687ec5729cc094a752759443c20fa227fb5de90.png", "thumbnail_height": 72, "thumbnail_width": 131}, "brand": {"id": "644924f54b696a1ba003bddb", "type": "brand", "url": "https://cars.chargetrip.io/5dcd60a6eec2cc1e12b95a78.png", "height": 432, "width": 768, "thumbnail_url": "https://cars.chargetrip.io/5dcd60a6eec2cc1e12b95a78-1573740730.png", "thumbnail_height": 24, "thumbnail_width": 56}, "video": {"id": None, "url": None}},
        "routing": {"fast_charging_support": True},
        "connect": {"providers": ["Enode"]},
    }
]


# -------------------------
# Modèles API
# -------------------------
class PlanRouteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: str = Field(..., alias="from")
    to: str
    vehicle_id: str


# -------------------------
# Utilitaires polyline (Google Encoded Polyline)
# -------------------------
def _decode_polyline(poly: str) -> List[Tuple[float, float]]:
    coords: List[Tuple[float, float]] = []
    index = 0
    lat = 0
    lng = 0

    while index < len(poly):
        shift = 0
        result = 0
        while True:
            b = ord(poly[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        shift = 0
        result = 0
        while True:
            b = ord(poly[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coords.append((lat / 1e5, lng / 1e5))

    return coords


def _encode_polyline(coords: List[Tuple[float, float]]) -> str:
    def _encode_value(v: int) -> str:
        v = ~(v << 1) if v < 0 else (v << 1)
        chunks = []
        while v >= 0x20:
            chunks.append(chr((0x20 | (v & 0x1F)) + 63))
            v >>= 5
        chunks.append(chr(v + 63))
        return "".join(chunks)

    last_lat = 0
    last_lng = 0
    out = []

    for lat, lng in coords:
        ilat = int(round(lat * 1e5))
        ilng = int(round(lng * 1e5))
        dlat = ilat - last_lat
        dlng = ilng - last_lng
        last_lat = ilat
        last_lng = ilng
        out.append(_encode_value(dlat))
        out.append(_encode_value(dlng))

    return "".join(out)


# -------------------------
# Géocodage et routage
# -------------------------
@dataclass
class GeoPoint:
    lat: float
    lon: float
    display_name: str


def geocode_nominatim(query: str) -> GeoPoint:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "info802-mini-projet/1.0 (student project)"}

    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise HTTPException(status_code=404, detail=f"Géocodage impossible pour: {query}")

    return GeoPoint(
        lat=float(data[0]["lat"]),
        lon=float(data[0]["lon"]),
        display_name=str(data[0].get("display_name", query)),
    )


def osrm_route(start: GeoPoint, end: GeoPoint) -> Dict[str, Any]:
    url = f"http://router.project-osrm.org/route/v1/driving/{start.lon},{start.lat};{end.lon},{end.lat}"
    params = {"overview": "full", "geometries": "polyline", "steps": "false"}

    r = requests.get(url, params=params, timeout=25)
    r.raise_for_status()
    js = r.json()

    if js.get("code") != "Ok" or not js.get("routes"):
        raise HTTPException(status_code=502, detail="OSRM n'a pas renvoyé de route exploitable.")

    route = js["routes"][0]
    return {
        "distance_m": float(route["distance"]),
        "duration_s": float(route["duration"]),
        "polyline": str(route["geometry"]),
    }


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def midpoint_along_polyline(coords: List[Tuple[float, float]]) -> Tuple[float, float]:
    # convenience wrapper for the common 50% case
    return point_along_polyline(coords, 0.5)


def point_along_polyline(coords: List[Tuple[float, float]], fraction: float) -> Tuple[float, float]:
    """Return the coordinates of a point located ``fraction`` of the way along
    the polyline defined by ``coords``. ``fraction`` must be between 0 and 1.

    The implementation is similar to ``midpoint_along_polyline`` but the
    target distance is scaled by the requested fraction.
    """
    if not coords:
        raise ValueError("coords list is empty")
    if len(coords) == 1 or fraction <= 0.0:
        return coords[0]
    if fraction >= 1.0:
        return coords[-1]

    # compute lengths of each segment and total length
    seg_lengths = []
    total = 0.0
    for i in range(len(coords) - 1):
        d = haversine_m(coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1])
        seg_lengths.append(d)
        total += d

    target = total * fraction
    acc = 0.0
    for i, d in enumerate(seg_lengths):
        if acc + d >= target:
            t = (target - acc) / max(d, 1e-9)
            lat = coords[i][0] + t * (coords[i + 1][0] - coords[i][0])
            lon = coords[i][1] + t * (coords[i + 1][1] - coords[i][1])
            return (lat, lon)
        acc += d

    return coords[-1]


# -------------------------
# Recherche borne IRVE (Opendatasoft)
# -------------------------
def search_irve_chargers(lat: float, lon: float, radius_m: int = 10000, rows: int = 12) -> List[Dict[str, Any]]:
    """Récupère les bornes IRVE avec l'API ODRE v2.1.

    L'API contient des coordonnées parfois inversées et le filtre spatial est peu
    fiable (il renvoie Breteuil alors qu'on cherche autour d'un point de la
    Bourgogne). Pour s'assurer de la validité des résultats on applique un
    filtrage local après récupération : on calcule nous-même la distance Haversine
    entre le point recherché et les coordonnées consolidées retournées et on
    rejette ceux qui dépassent `radius_m`.
    """
    url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/bornes-irve/records"
    params = {
        # on envoie quand même le filtre au serveur pour limiter les résultats
        # mais l'ordre des coordonnées ne semble pas fiable, on gardera donc
        # un rayon large en pratique (voir plus bas)
        "geofilter.distance": f"{lon},{lat},{radius_m}",
        "limit": rows,
        "order_by": "puissance_nominale DESC"
    }

    r = requests.get(url, params=params, timeout=25)
    r.raise_for_status()
    js = r.json()
    recs = js.get("results", [])

    out = []
    for rec in recs:
        lat2 = rec.get("consolidated_latitude") or rec.get("latitude")
        lon2 = rec.get("consolidated_longitude") or rec.get("longitude")
        if lat2 is None or lon2 is None:
            continue
        try:
            lat2 = float(lat2)
            lon2 = float(lon2)
        except (TypeError, ValueError):
            continue

        # distance réelle entre le centre demandé et la borne
        d = haversine_m(lat, lon, lat2, lon2)
        if d > radius_m:
            # ignorer les points trop loin (correction de l'API spatiale)
            continue

        out.append({
            "recordid": rec.get("recordid"),
            "datasetid": rec.get("datasetid"),
            "name": rec.get("nom_station") or rec.get("name") or "Borne IRVE",
            "operator": rec.get("nom_operateur") or rec.get("operator"),
            "address": rec.get("adresse_station") or rec.get("adresse") or "",
            "power_kw": float(rec.get("puissance_nominale") or 0.0),
            "pdc_count": int(rec.get("nbre_pdc") or 0),
            "payment_cb": str(rec.get("paiement_cb", "")),
            "fields": rec,
            "position": {"lat": lat2, "lon": lon2},
        })
    return out


def min_distance_to_route(coords: List[Tuple[float, float]], lat: float, lon: float) -> float:
    """Return the minimum haversine distance (in meters) between a point and any
    vertex of the route polyline. This is a very simple approximation but
    sufficient for filtering out chargers that lie far off the route.
    """
    if not coords:
        return float("inf")

    best = float("inf")
    for clat, clon in coords:
        d = haversine_m(lat, lon, clat, clon)
        if d < best:
            best = d
    return best


def _cumulative_lengths(coords: List[Tuple[float, float]]) -> List[float]:
    """Return cumulative distances (meters) at each polyline vertex.

    cumulative[0] == 0.0, cumulative[i] is distance from start to coords[i].
    """
    cum: List[float] = [0.0]
    if not coords:
        return cum
    total = 0.0
    for i in range(len(coords) - 1):
        d = haversine_m(coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1])
        total += d
        cum.append(total)
    return cum


def _nearest_route_index(coords: List[Tuple[float, float]], lat: float, lon: float) -> int:
    """Return index of the route vertex closest to the given point."""
    best_i = 0
    best_d = float("inf")
    for i, (clat, clon) in enumerate(coords):
        d = haversine_m(lat, lon, clat, clon)
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


# -------------------------
# SOAP Service Client
# -------------------------
def calculate_trip_time_soap(
    distance_km: float,
    autonomy_km: float,
    avg_speed_kmh: float,
    charge_time_min_per_stop: int
) -> Dict[str, Any]:
    """Call SOAP TripTime service to calculate journey time.
    
    Returns: {\"stops\": int, \"drive_time_min\": float, \"charge_time_min_total\": float, \"total_time_min\": float, \"message\": str}
    """
    try:
        # Call SOAP service directly in-memory (no HTTP)
        service = TripTimeService()
        result = service.estimate_trip_time(
            distance_km=distance_km,
            autonomy_km=autonomy_km,
            avg_speed_kmh=avg_speed_kmh,
            charge_time_min_per_stop=charge_time_min_per_stop
        )
        return {
            "stops": int(result.stops),
            "drive_time_min": float(result.drive_time_min),
            "charge_time_min_total": float(result.charge_time_min_total),
            "total_time_min": float(result.total_time_min),
            "message": str(result.message)
        }
    except Exception as e:
        # Fallback: calculate locally if SOAP unavailable
        stops = max(int(math.ceil(distance_km / autonomy_km)) - 1, 0)
        drive_time_min = (distance_km / avg_speed_kmh) * 60.0
        charge_time_min_total = float(stops * charge_time_min_per_stop)
        total_time_min = drive_time_min + charge_time_min_total
        return {
            "stops": stops,
            "drive_time_min": drive_time_min,
            "charge_time_min_total": charge_time_min_total,
            "total_time_min": total_time_min,
            "message": f"Fallback (SOAP error: {str(e)})"
        }


def choose_best_charger(
    chargers: List[Dict[str, Any]],
    route_coords: Optional[List[Tuple[float, float]]] = None,
    max_offroute: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """Return the ``best`` charger from the list.

    The original implementation only considered power and payment-by-card
    availability.  We now optionally accept a list of coordinates representing
    the planned route; if provided we filter out any chargers whose closest
    approach to the route exceeds ``max_offroute`` (meters).  We also slightly
    penalise candidates that are farther from the route when computing the
    score, to prefer chargers that lie along the itinerary.
    """
    if not chargers:
        return None

    def route_dist(c: Dict[str, Any]) -> float:
        if route_coords is None:
            return 0.0
        pos = c.get("position", {})
        return min_distance_to_route(route_coords, pos.get("lat", 0.0), pos.get("lon", 0.0))

    # filter by distance if requested
    if route_coords is not None and max_offroute is not None:
        chargers = [c for c in chargers if route_dist(c) <= max_offroute]

    if not chargers:
        return None

    def score(c: Dict[str, Any]) -> float:
        p = float(c.get("power_kw", 0.0))
        cb = 1.0 if str(c.get("payment_cb", "")).lower() == "true" else 0.0
        # subtract a small amount proportional to distance to favour on-route
        return p + 5.0 * cb - 1e-4 * route_dist(c)

    return sorted(chargers, key=score, reverse=True)[0]


# -------------------------
# Endpoint principal /api/plan-route
# -------------------------
@router.post("/plan-route")
def plan_route(req: PlanRouteRequest) -> Dict[str, Any]:
    vehicle = VEHICLES.get(req.vehicle_id)
    if not vehicle:
        # Try to derive a lightweight vehicle profile from VEHICLE_LIST when
        # the frontend sends an id from the richer dataset.
        vitem = next((v for v in VEHICLE_LIST if v.get("id") == req.vehicle_id), None)
        if vitem:
            # build a minimal vehicle profile compatible with existing planner
            best_range = vitem.get("range", {}).get("chargetrip_range", {}).get("best")
            try:
                range_km = int(best_range) if best_range is not None else 250
            except Exception:
                range_km = 250

            vehicle = {
                "id": vitem.get("id"),
                "brand": vitem.get("naming", {}).get("make"),
                "model": vitem.get("naming", {}).get("model"),
                "rangeKm": range_km,
                "avgSpeedKmh": 110,
                "chargeTimeMin": 25,
            }
        else:
            raise HTTPException(status_code=404, detail=f"Véhicule inconnu: {req.vehicle_id}")

    start = geocode_nominatim(req.from_)
    end = geocode_nominatim(req.to)

    # 1) route directe pour estimation
    direct = osrm_route(start, end)
    direct_coords = _decode_polyline(direct["polyline"])
    mid_lat, mid_lon = midpoint_along_polyline(direct_coords)

    # 2) calculer le nombre d'arrêts nécessaires en fonction de l'autonomie du
    # véhicule et tenter de planifier ces arrêts le long de la polyline.
    # On utilise une stratégie simple : si la distance totale est D et
    # l'autonomie R (km), il faut n = ceil(D/R)-1 arrêts. On place ces arrêts
    # aux fractions i/(n+1) le long du trajet et on recherche une borne proche
    # de chaque point. Si la recherche échoue pour tous les arrêts, on retombe
    # sur la stratégie antérieure (1 arrêt au milieu).
    vehicle_range_km = float(vehicle.get("rangeKm", 250))
    total_km = direct["distance_m"] / 1000.0
    needed_stops = max(0, math.ceil(total_km / vehicle_range_km) - 1)

    stops_found: List[Dict[str, float]] = []
    chargers_payload: List[Dict[str, Any]] = []

    MAX_OFFROUTE_M = 50_000

    if needed_stops > 0:
        # corridor-based strategy: sample many points along the route, gather
        # nearby chargers into a candidate pool, then greedily select stops
        # such that no driving leg exceeds the vehicle range.
        failed = False
        sample_count = max(20, (needed_stops + 1) * 6)
        candidates_map: Dict[str, Dict[str, Any]] = {}

        for si in range(sample_count):
            frac = si / max(1, sample_count - 1)
            lat0, lon0 = point_along_polyline(direct_coords, frac)
            for radius in (20_000, 50_000, 100_000, 200_000):
                chs = search_irve_chargers(lat0, lon0, radius_m=radius, rows=50)
                for ch in chs:
                    rid = ch.get("recordid") or f"{ch.get('position',{}).get('lat')}_{ch.get('position',{}).get('lon')}"
                    if rid not in candidates_map:
                        c = dict(ch)
                        c["search_radius_used"] = radius
                        candidates_map[rid] = c

        if not candidates_map:
            failed = True
        else:
            candidates = list(candidates_map.values())
            cum = _cumulative_lengths(direct_coords)
            total_len = cum[-1] if cum else 0.0

            # annotate candidates with route index and cumulative distance
            for c in candidates:
                latc = float(c["position"]["lat"])
                lonc = float(c["position"]["lon"])
                idx = _nearest_route_index(direct_coords, latc, lonc)
                c["_route_index"] = idx
                c["_cumdist_m"] = cum[idx] if idx < len(cum) else 0.0
                c["_route_distance_m"] = min_distance_to_route(direct_coords, latc, lonc)

            # greedy selection: from start, pick the farthest reachable charger within range
            last_pos = 0.0
            max_leg = vehicle_range_km * 1000.0
            selected: List[Dict[str, float]] = []
            selected_payload: List[Dict[str, Any]] = []

            while last_pos + max_leg < total_len:
                # candidates ahead within range
                possible = [c for c in candidates if c["_cumdist_m"] > last_pos and (c["_cumdist_m"] - last_pos) <= max_leg]
                if not possible:
                    # allow some slack (50 km) to tolerate sparse networks
                    slack = 50_000
                    possible = [c for c in candidates if c["_cumdist_m"] > last_pos and (c["_cumdist_m"] - last_pos) <= (max_leg + slack)]
                    if not possible:
                        failed = True
                        break

                # prefer chargers farther along the route but with good power
                possible = sorted(possible, key=lambda c: (c.get("_cumdist_m", 0.0), float(c.get("power_kw", 0.0))), reverse=True)
                pick = possible[0]
                # record pick
                stop_lat = float(pick["position"]["lat"])
                stop_lon = float(pick["position"]["lon"])
                selected.append({"lat": stop_lat, "lon": stop_lon})
                selected_payload.append({
                    "stop": {"lat": stop_lat, "lon": stop_lon},
                    "charger": {
                        "recordid": pick.get("recordid"),
                        "datasetid": pick.get("datasetid"),
                        "name": pick.get("name"),
                        "operator": pick.get("operator"),
                        "address": pick.get("address"),
                        "power_kw": pick.get("power_kw"),
                        "pdc_count": pick.get("pdc_count"),
                        "payment_cb": pick.get("payment_cb"),
                        "position": pick.get("position"),
                        "search_radius_m": pick.get("search_radius_used"),
                        "route_distance_m": pick.get("_route_distance_m"),
                    },
                })

                last_pos = pick.get("_cumdist_m", last_pos)
                # remove used candidate
                candidates = [c for c in candidates if c != pick]

            if not failed and len(selected) > 0:
                # build multi-leg route start -> stops -> end
                points = [GeoPoint(lat=start.lat, lon=start.lon, display_name=start.display_name)]
                for s in selected:
                    points.append(GeoPoint(lat=s["lat"], lon=s["lon"], display_name="Stop (borne)"))
                points.append(GeoPoint(lat=end.lat, lon=end.lon, display_name=end.display_name))

                total_distance_m = 0.0
                total_duration_s = 0.0
                all_coords: List[Tuple[float, float]] = []
                for j in range(len(points) - 1):
                    p1 = points[j]
                    p2 = points[j + 1]
                    leg = osrm_route(p1, p2)
                    coords_leg = _decode_polyline(leg["polyline"])
                    if not all_coords:
                        all_coords = coords_leg
                    else:
                        if all_coords[-1] == coords_leg[0]:
                            all_coords += coords_leg[1:]
                        else:
                            all_coords += coords_leg
                    total_distance_m += leg["distance_m"]
                    total_duration_s += leg["duration_s"]

                poly = _encode_polyline(all_coords)
                # Call SOAP service for trip time calculation
                avg_speed_kmh = vehicle.get("avgSpeedKmh", 100)
                charge_time_min_per_stop = vehicle.get("chargeTimeMin", 25)
                soap_result = calculate_trip_time_soap(
                    total_distance_m / 1000.0,
                    vehicle_range_km,
                    avg_speed_kmh,
                    charge_time_min_per_stop
                )
                drive_time_min = soap_result["drive_time_min"]
                charge_time_min_total = soap_result["charge_time_min_total"]
                total_time_min = soap_result["total_time_min"]

                return {
                    "input": {
                        "from": req.from_,
                        "to": req.to,
                        "vehicle_id": req.vehicle_id,
                        "start": {"display_name": start.display_name, "lat": start.lat, "lon": start.lon},
                        "end": {"display_name": end.display_name, "lat": end.lat, "lon": end.lon},
                    },
                    "vehicle": vehicle,
                    "route": {
                        "distance_km": round(total_distance_m / 1000.0, 3),
                        "duration_min": round(total_duration_s / 60.0, 3),
                        "points_count": len(all_coords),
                        "polyline": poly,
                    },
                    "stop_points": selected,
                    "chargers": selected_payload,
                    "time": {
                        "message": "OK",
                        "stops": len(selected),
                        "drive_time_min": drive_time_min,
                        "charge_time_min_total": charge_time_min_total,
                        "total_time_min": total_time_min,
                    },
                }
        # else fallthrough to single-stop approach below

    # If we reached here, either needed_stops was 0 or multi-stop attempt failed.
    # Try single-stop fallback: search around the midpoint progressively.
    charger = None
    for radius in (10_000, 20_000, 50_000, 100_000, 200_000):
        chs = search_irve_chargers(mid_lat, mid_lon, radius_m=radius, rows=15)
        charger = choose_best_charger(chs, route_coords=direct_coords, max_offroute=MAX_OFFROUTE_M)
        if charger:
            break

    stop_points: List[Dict[str, float]] = []
    chargers_payload: List[Dict[str, Any]] = []

    if charger:
        stop_lat = float(charger["position"]["lat"])
        stop_lon = float(charger["position"]["lon"])
        stop_points.append({"lat": stop_lat, "lon": stop_lon})
        # calcul de la distance réelle entre la borne et la route pour trace
        route_dist = min_distance_to_route(direct_coords, stop_lat, stop_lon)

        chargers_payload.append({
            "stop": {"lat": stop_lat, "lon": stop_lon},
            "charger": {
                "recordid": charger.get("recordid"),
                "datasetid": charger.get("datasetid"),
                "name": charger.get("name"),
                "operator": charger.get("operator"),
                "address": charger.get("address"),
                "power_kw": charger.get("power_kw"),
                "pdc_count": charger.get("pdc_count"),
                "payment_cb": charger.get("payment_cb"),
                "position": charger.get("position"),
                "search_radius_m": radius,
                "route_distance_m": route_dist,
            },
        })

        # recalcul start->stop->end
        stop = GeoPoint(lat=stop_lat, lon=stop_lon, display_name="Stop (borne)")
        part1 = osrm_route(start, stop)
        part2 = osrm_route(stop, end)

        coords1 = _decode_polyline(part1["polyline"])
        coords2 = _decode_polyline(part2["polyline"])
        if coords1 and coords2 and coords1[-1] == coords2[0]:
            coords = coords1 + coords2[1:]
        else:
            coords = coords1 + coords2

        poly = _encode_polyline(coords)
        total_distance_m = part1["distance_m"] + part2["distance_m"]
        total_duration_s = part1["duration_s"] + part2["duration_s"]

        # Call SOAP service for trip time calculation
        avg_speed_kmh = vehicle.get("avgSpeedKmh", 100)
        charge_time_min_per_stop = vehicle.get("chargeTimeMin", 25)
        soap_result = calculate_trip_time_soap(
            total_distance_m / 1000.0,
            vehicle_range_km,
            avg_speed_kmh,
            charge_time_min_per_stop
        )
        drive_time_min = soap_result["drive_time_min"]
        charge_time_min_total = soap_result["charge_time_min_total"]
        total_time_min = soap_result["total_time_min"]

        return {
            "input": {
                "from": req.from_,
                "to": req.to,
                "vehicle_id": req.vehicle_id,
                "start": {"display_name": start.display_name, "lat": start.lat, "lon": start.lon},
                "end": {"display_name": end.display_name, "lat": end.lat, "lon": end.lon},
            },
            "vehicle": vehicle,
            "route": {
                "distance_km": round(total_distance_m / 1000.0, 3),
                "duration_min": round(total_duration_s / 60.0, 3),
                "points_count": len(coords),
                "polyline": poly,
            },
            "stop_points": stop_points,
            "chargers": chargers_payload,
            "time": {
                "message": "OK",
                "stops": 1,
                "drive_time_min": drive_time_min,
                "charge_time_min_total": charge_time_min_total,
                "total_time_min": total_time_min,
            },
        }
    else:
        # aucune borne trouvée
        # Call SOAP service for trip time calculation (no charging stops)
        avg_speed_kmh = vehicle.get("avgSpeedKmh", 100)
        charge_time_min_per_stop = vehicle.get("chargeTimeMin", 25)
        soap_result = calculate_trip_time_soap(
            direct["distance_m"] / 1000.0,
            vehicle_range_km,
            avg_speed_kmh,
            charge_time_min_per_stop
        )
        drive_time_min = soap_result["drive_time_min"]
        charge_time_min_total = soap_result["charge_time_min_total"]
        total_time_min = soap_result["total_time_min"]
        return {
            "input": {
                "from": req.from_,
                "to": req.to,
                "vehicle_id": req.vehicle_id,
                "start": {"display_name": start.display_name, "lat": start.lat, "lon": start.lon},
                "end": {"display_name": end.display_name, "lat": end.lat, "lon": end.lon},
            },
            "vehicle": vehicle,
            "route": {
                "distance_km": round(direct["distance_m"] / 1000.0, 3),
                "duration_min": round(direct["duration_s"] / 60.0, 3),
                "points_count": len(direct_coords),
                "polyline": direct["polyline"],
            },
            "stop_points": [],
            "chargers": [],
            "time": {
                "message": "OK (aucune borne trouvée)",
                "stops": soap_result["stops"],
                "drive_time_min": drive_time_min,
                "charge_time_min_total": charge_time_min_total,
                "total_time_min": total_time_min,
            },
        }


# --------------------------------------------------------------------
# GraphQL MINIMALISTE "MAISON"
# --------------------------------------------------------------------
# On accepte le POST JSON : { "query": "query { vehicles { ... } }" }
# et on répond avec { "data": { "vehicles": [...] } }
# Assez pour ton front, sans dépendance strawberry.
# --------------------------------------------------------------------
graphql_router = APIRouter(tags=["graphql"])


class GraphQLBody(BaseModel):
    query: str


@graphql_router.post("/graphql")
def graphql_endpoint(body: GraphQLBody) -> Dict[str, Any]:
    q = (body.query or "").lower()
    # Support a small set of queries for the front-end:
    # - "vehicles" (existing simple list)
    # - "vehiclelist" richer dataset (Chargetrip-like)
    if "vehiclelist" in q:
        # Allow extending the small built-in VEHICLE_LIST with an optional
        # local dataset `graphql_vehicles.data.VEHICLES` if present. This
        # lets the developer drop a larger list into `graphql_vehicles`.
        extra = []
        try:
            from graphql_vehicles import data as gvdata
            for v in getattr(gvdata, "VEHICLES", []):
                # convert small vehicle shape to minimal chargetrip-like entry
                vid = v.get("id")
                range_best = v.get("range_km") or v.get("rangeKm") or None
                extra.append({
                    "id": vid,
                    "naming": {"make": v.get("brand"), "model": v.get("model"), "version": None, "edition": None, "chargetrip_version": None},
                    "range": {"chargetrip_range": {"best": range_best}},
                    "media": {"image": {"thumbnail_url": None}},
                })
        except Exception:
            extra = []

        # return the richer built-in list plus any local extras
        merged = VEHICLE_LIST + extra
        return {"data": {"vehicleList": merged}}

    if "vehicles" in q:
        vehicles = list(VEHICLES.values())
        return {"data": {"vehicles": vehicles}}

    return {"errors": [{"message": "Only 'vehicles' or 'vehicleList' queries are supported in this mini GraphQL endpoint."}]}

    # On renvoie tous les champs attendus par ton front.
    return {
        "data": {
            "vehicles": [
                {
                    "id": v["id"],
                    "brand": v["brand"],
                    "model": v["model"],
                    "rangeKm": int(v["rangeKm"]),
                    "avgSpeedKmh": int(v["avgSpeedKmh"]),
                    "chargeTimeMin": int(v["chargeTimeMin"]),
                }
                for v in vehicles
            ]
        }
    }