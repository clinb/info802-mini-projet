from typing import List, Optional
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from data import VEHICLES


@strawberry.type
class Vehicle:
    id: str
    brand: str
    model: str
    range_km: int
    avg_speed_kmh: int
    charge_time_min: int


def _to_vehicle(d: dict) -> Vehicle:
    return Vehicle(
        id=d["id"],
        brand=d["brand"],
        model=d["model"],
        range_km=int(d["range_km"]),
        avg_speed_kmh=int(d["avg_speed_kmh"]),
        charge_time_min=int(d["charge_time_min"]),
    )


@strawberry.type
class Query:
    @strawberry.field
    def vehicles(self) -> List[Vehicle]:
        return [_to_vehicle(v) for v in VEHICLES]

    @strawberry.field
    def vehicle_by_id(self, id: str) -> Optional[Vehicle]:
        for v in VEHICLES:
            if v["id"] == id:
                return _to_vehicle(v)
        return None


schema = strawberry.Schema(query=Query)

app = FastAPI(title="Vehicles GraphQL")
app.include_router(GraphQLRouter(schema), prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8004, reload=True)