import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Configuration:
    # SOAP
    url_wsdl_service_temps: str = os.getenv(
        "URL_WSDL_SERVICE_TEMPS",
        "http://127.0.0.1:8001/?wsdl"
    )

    # Open-street
    openstreet_api_key: str = os.getenv("OPENSTREET_API_KEY", "")
    openstreet_base_url: str = os.getenv("OPENSTREET_BASE_URL", "https://maps.open-street.com/api")


CONFIG = Configuration()