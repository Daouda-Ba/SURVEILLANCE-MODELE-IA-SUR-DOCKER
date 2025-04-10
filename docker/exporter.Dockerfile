FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
RUN pip install --no-cache-dir flask prometheus_client psutil requests

# Exposer le port pour les métriques
EXPOSE 8000

# Lancer l'exportateur de métriques
CMD ["python", "/app/exporter.py"]