FROM python:3.11-slim

WORKDIR /app

# Installer les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port Streamlit
EXPOSE 8501

# Lancer l'application Streamlit
CMD ["streamlit", "run", "/app/app.py", "--server.address=0.0.0.0"]