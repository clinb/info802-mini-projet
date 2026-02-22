from pydantic import BaseModel, Field


class RequeteTempsTrajet(BaseModel):
    distance_km: float = Field(..., gt=0)
    autonomie_km: int = Field(..., gt=0)
    temps_recharge_min: int = Field(..., gt=0)


class ReponseTempsTrajet(BaseModel):
    temps_total_min: int


class Coordonnees(BaseModel):
    lat: float
    lng: float


class RequeteItineraire(BaseModel):
    ville_depart: str = Field(..., min_length=1)
    ville_arrivee: str = Field(..., min_length=1)


class ReponseItineraire(BaseModel):
    depart: Coordonnees
    arrivee: Coordonnees
    distance_km: float
    polyline: str