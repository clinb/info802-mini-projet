import zeep


class ClientServiceTempsSOAP:
    def __init__(self, url_wsdl: str):
        self._client = zeep.Client(wsdl=url_wsdl)

    def calculer_temps_trajet(self, distance_km: float, autonomie_km: int, temps_recharge_min: int) -> int:
        # Le nom exact de la méthode correspond à celle exposée par le service SOAP
        # (calcul_temps_trajet dans notre serveur Spyne).
        return int(self._client.service.calcul_temps_trajet(distance_km, autonomie_km, temps_recharge_min))