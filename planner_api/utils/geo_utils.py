import math
from typing import List, Tuple

Point = Tuple[float, float]  # (lat, lon)

def haversine_km(a: Point, b: Point) -> float:
    lat1, lon1 = a
    lat2, lon2 = b
    r = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    s = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(s))

def pick_stop_points_along_polyline(points: List[Point], nb_stops: int) -> List[Point]:
    """
    Sélectionne nb_stops points à peu près équidistants le long de la polyline.
    Approche simple et robuste pour TP.
    """
    if nb_stops <= 0 or len(points) < 2:
        return []

    # longueur cumulée
    cum = [0.0]
    for i in range(1, len(points)):
        cum.append(cum[-1] + haversine_km(points[i - 1], points[i]))

    total = cum[-1]
    if total <= 0:
        return []

    targets = [(k * total) / (nb_stops + 1) for k in range(1, nb_stops + 1)]
    res: List[Point] = []

    j = 0
    for t in targets:
        while j < len(cum) - 1 and cum[j] < t:
            j += 1
        res.append(points[j])

    return res