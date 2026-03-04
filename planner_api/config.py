import os

SOAP_WSDL_URL = os.getenv("SOAP_WSDL_URL", "http://localhost:8003/?wsdl")
GRAPHQL_URL = os.getenv("GRAPHQL_URL", "http://localhost:8004/graphql")

# Nominatim (OpenStreetMap) - pas de clé
NOMINATIM_URL = os.getenv("NOMINATIM_URL", "https://nominatim.openstreetmap.org/search")

# OSRM public - pas de clé
OSRM_URL = os.getenv("OSRM_URL", "https://router.project-osrm.org/route/v1/driving")

# IRVE (OpenDataSoft) - à adapter si besoin
IRVE_BASE_URL = os.getenv(
    "IRVE_BASE_URL",
    "https://odre.opendatasoft.com/api/records/1.0/search/"
)
IRVE_DATASET = os.getenv("IRVE_DATASET", "bornes-irve")
IRVE_RADIUS_M = int(os.getenv("IRVE_RADIUS_M", "5000"))