import requests


class GraphQLVehiclesClient:
    def __init__(self, graphql_url: str):
        self.graphql_url = graphql_url

    def get_vehicle_by_id(self, vehicle_id: str) -> dict | None:
        query = """
        query GetVehicle($id: String!) {
          vehicleById(id: $id) {
            id
            brand
            model
            rangeKm
            avgSpeedKmh
            chargeTimeMin
          }
        }
        """
        variables = {"id": vehicle_id}

        r = requests.post(
            self.graphql_url,
            json={"query": query, "variables": variables},
            timeout=10,
        )
        r.raise_for_status()
        payload = r.json()

        if "errors" in payload:
            raise RuntimeError(f"GraphQL errors: {payload['errors']}")

        data = payload.get("data", {})
        return data.get("vehicleById")