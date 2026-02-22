import logging

from spyne import Application
from spyne.decorator import srpc
from spyne.service import ServiceBase
from spyne.model.primitive import Integer, Float
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


class ServiceTempsTrajet(ServiceBase):

    @srpc(Float, Integer, Integer, _returns=Integer)
    def calcul_temps_trajet(distance_km, autonomie_km, temps_recharge_min):
        """
        distance_km : distance totale du trajet
        autonomie_km : autonomie maximale du véhicule
        temps_recharge_min : temps nécessaire pour une recharge complète
        """

        vitesse_moyenne = 90  # hypothèse simplifiée (km/h)

        temps_conduite_h = distance_km / vitesse_moyenne

        # nombre de recharges nécessaires
        nb_recharges = int(distance_km / autonomie_km)

        temps_recharge_h = nb_recharges * (temps_recharge_min / 60)

        temps_total_minutes = round((temps_conduite_h + temps_recharge_h) * 60)

        return temps_total_minutes


application = Application(
    [ServiceTempsTrajet],
    tns="tp.ve.service.temps",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)

wsgi_application = WsgiApplication(application)


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.INFO)

    serveur = make_server("0.0.0.0", 8001, wsgi_application)
    print("Service SOAP démarré sur http://127.0.0.1:8001")
    print("WSDL disponible sur http://127.0.0.1:8001/?wsdl")

    serveur.serve_forever()