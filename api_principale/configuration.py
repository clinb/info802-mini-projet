import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Configuration:
    url_wsdl_service_temps: str = os.getenv("URL_WSDL_SERVICE_TEMPS", "http://127.0.0.1:8001/?wsdl")


CONFIG = Configuration()