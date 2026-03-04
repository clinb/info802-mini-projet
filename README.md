# TP Véhicules électriques – base services (SOAP + GraphQL + REST)

## 1) Lancer SOAP TripTime
cd soap_triptime
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
WSDL: http://localhost:8003/?wsdl

## 2) Lancer GraphQL Vehicles
cd ../graphql_vehicles
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
GraphQL: http://localhost:8004/graphql

## 3) Lancer Planner API (REST)
cd ../planner_api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
REST: http://localhost:8000