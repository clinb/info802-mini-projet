from fastapi import FastAPI, HTTPException

from api_principale.configuration import CONFIG
from api_principale.schemas import RequeteTempsTrajet, ReponseTempsTrajet
from api_principale.services_externes.service_temps_soap import ClientServiceTempsSOAP

app = FastAPI(title="TP Véhicules Électriques - API Principale")


@app.get("/ping")
def ping():
    return {"statut": "ok"}


@app.post("/temps_trajet", response_model=ReponseTempsTrajet)
def temps_trajet(requete: RequeteTempsTrajet):
    try:
        client = ClientServiceTempsSOAP(CONFIG.url_wsdl_service_temps)
        temps_total = client.calculer_temps_trajet(
            distance_km=requete.distance_km,
            autonomie_km=requete.autonomie_km,
            temps_recharge_min=requete.temps_recharge_min,
        )
        return ReponseTempsTrajet(temps_total_min=temps_total)

    except Exception as e:
        # On reste volontairement simple pour le TP : si SOAP est down ou WSDL incorrect, on renvoie 502.
        raise HTTPException(status_code=502, detail=f"Erreur appel service SOAP: {e}")