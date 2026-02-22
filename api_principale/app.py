from fastapi import FastAPI, HTTPException

from api_principale.configuration import CONFIG
from api_principale.schemas import RequeteTempsTrajet, ReponseTempsTrajet
from api_principale.services_externes.service_temps_soap import ClientServiceTempsSOAP
from api_principale.services_externes.service_geocodage import ServiceGeocodageOpenStreet
from api_principale.services_externes.service_itineraire import ServiceItineraireOpenStreet
from api_principale.schemas import RequeteItineraire, ReponseItineraire, Coordonnees

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

@app.post("/itineraire", response_model=ReponseItineraire)
def itineraire(requete: RequeteItineraire):
    if not CONFIG.openstreet_api_key:
        raise HTTPException(status_code=500, detail="OPENSTREET_API_KEY manquante dans le .env")

    try:
        geo = ServiceGeocodageOpenStreet(CONFIG.openstreet_base_url, CONFIG.openstreet_api_key)
        route = ServiceItineraireOpenStreet(CONFIG.openstreet_base_url, CONFIG.openstreet_api_key)

        depart_lat, depart_lng = geo.geocoder_ville(requete.ville_depart)
        arrivee_lat, arrivee_lng = geo.geocoder_ville(requete.ville_arrivee)

        data_route = route.calculer_itineraire(depart_lat, depart_lng, arrivee_lat, arrivee_lng)

        polyline = data_route.get("polyline")
        if not polyline:
            raise ValueError("Réponse route sans 'polyline'")

        # Selon les APIs, la distance peut être à différents endroits.
        # On fait simple : on essaie quelques clés courantes, sinon -1.
        distance_km = None
        for key in ("distance", "distance_km", "dist"):
            if key in data_route:
                distance_km = float(data_route[key])
                break

        # fallback : parfois dans "routes[0].distance" en mètres (selon services)
        if distance_km is None and isinstance(data_route.get("routes"), list) and data_route["routes"]:
            d = data_route["routes"][0].get("distance")
            if d is not None:
                # supposition “mètres” -> km
                distance_km = float(d) / 1000.0

        if distance_km is None:
            # on ne bloque pas le TP : on renvoie quand même la polyline
            distance_km = -1.0

        return ReponseItineraire(
            depart=Coordonnees(lat=depart_lat, lng=depart_lng),
            arrivee=Coordonnees(lat=arrivee_lat, lng=arrivee_lng),
            distance_km=distance_km,
            polyline=polyline,
        )

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur itinéraire (Open-street): {e}")