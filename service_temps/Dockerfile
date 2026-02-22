FROM python:3.11-slim

WORKDIR /app

COPY serveur_soap.py /app/serveur_soap.py

RUN pip install --no-cache-dir spyne lxml

EXPOSE 8001

CMD ["python", "/app/serveur_soap.py"]