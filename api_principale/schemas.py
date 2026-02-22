from pydantic import BaseModel, Field


class RequeteTempsTrajet(BaseModel):
    distance_km: float = Field(..., gt=0)
    autonomie_km: int = Field(..., gt=0)
    temps_recharge_min: int = Field(..., gt=0)


class ReponseTempsTrajet(BaseModel):
    temps_total_min: int