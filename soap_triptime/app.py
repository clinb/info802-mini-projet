import math
from spyne import Application, rpc, ServiceBase, Float, Integer, Unicode, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


class TripTimeResult(ComplexModel):
    stops = Integer
    drive_time_min = Float
    charge_time_min_total = Float
    total_time_min = Float
    message = Unicode


class TripTimeService(ServiceBase):
    @rpc(
        Float,  # distance_km
        Float,  # autonomy_km
        Float,  # avg_speed_kmh
        Integer,  # charge_time_min_per_stop
        _returns=TripTimeResult
    )
    def estimate_trip_time(ctx, distance_km, autonomy_km, avg_speed_kmh, charge_time_min_per_stop):
        res = TripTimeResult()

        # Validation simple
        if distance_km is None or autonomy_km is None or avg_speed_kmh is None or charge_time_min_per_stop is None:
            res.message = "Missing parameter(s)"
            res.stops = 0
            res.drive_time_min = 0.0
            res.charge_time_min_total = 0.0
            res.total_time_min = 0.0
            return res

        if distance_km < 0 or autonomy_km <= 0 or avg_speed_kmh <= 0 or charge_time_min_per_stop < 0:
            res.message = "Invalid parameter(s)"
            res.stops = 0
            res.drive_time_min = 0.0
            res.charge_time_min_total = 0.0
            res.total_time_min = 0.0
            return res

        # Nombre d'arrêts : si distance <= autonomie => 0, sinon ceil(distance/autonomie)-1
        stops = max(int(math.ceil(distance_km / autonomy_km)) - 1, 0)

        drive_time_min = (distance_km / avg_speed_kmh) * 60.0
        charge_time_min_total = float(stops * charge_time_min_per_stop)
        total_time_min = drive_time_min + charge_time_min_total

        res.message = "OK"
        res.stops = stops
        res.drive_time_min = float(drive_time_min)
        res.charge_time_min_total = float(charge_time_min_total)
        res.total_time_min = float(total_time_min)
        return res


application = Application(
    [TripTimeService],
    tns="info802.triptime.soap",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    host = "0.0.0.0"
    port = 8003
    print(f"SOAP TripTime running on http://{host}:{port}")
    print("WSDL: http://localhost:8003/?wsdl")
    server = make_server(host, port, wsgi_app)
    server.serve_forever()