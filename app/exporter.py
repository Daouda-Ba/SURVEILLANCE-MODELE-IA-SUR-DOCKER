from flask import Flask, request, Response, jsonify
import psutil
import time
import threading
import os
from prometheus_client import start_http_server, Counter, Gauge, Summary, REGISTRY, generate_latest

app = Flask(__name__)

# Définir métriques Prometheus
prediction_requests = Counter('model_prediction_requests_total', 'Nombre total de demandes de prédiction')
prediction_results = Counter('model_prediction_results_total', 'Résultats des prédictions', ['result'])
prediction_errors = Counter('model_prediction_errors_total', 'Nombre d\'erreurs de prédiction')
model_latency = Summary('model_prediction_latency_seconds', 'Temps de prédiction du modèle')

# Métriques système
cpu_usage = Gauge('system_cpu_usage_percent', 'Utilisation CPU en pourcentage')
memory_usage = Gauge('system_memory_usage_bytes', 'Utilisation mémoire en bytes')
memory_percent = Gauge('system_memory_usage_percent', 'Pourcentage de mémoire utilisée')

# Endpoint pour recevoir les mises à jour de métriques de l'application Streamlit
@app.route('/update', methods=['POST'])
def update_metric():
    data = request.json
    
    if not data or 'name' not in data or 'value' not in data:
        return jsonify({"status": "error", "message": "Invalid data format"}), 400
    
    name = data['name']
    value = float(data['value'])
    labels = data.get('labels', {})
    
    # Mettre à jour la métrique appropriée
    if name == 'prediction_requests_total':
        prediction_requests.inc(value)
    elif name == 'model_prediction_latency_seconds':
        model_latency.observe(value)
    elif name == 'model_prediction_results':
        prediction_results.labels(**labels).inc(value)
    elif name == 'model_prediction_errors':
        prediction_errors.inc(value)
    
    return jsonify({"status": "success"}), 200

# Endpoint pour exposer les metriques au format Prometheus
@app.route('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), mimetype="text/plain")

# Fonction pour mettre a jour les métriques système
def update_system_metrics():
    while True:
        cpu_usage.set(psutil.cpu_percent())
        memory_usage.set(psutil.virtual_memory().used)
        memory_percent.set(psutil.virtual_memory().percent)
        time.sleep(1)

if __name__ == '__main__':
    # Démarrer la mise à jour des métriques système dans un thread séparé
    metrics_thread = threading.Thread(target=update_system_metrics, daemon=True)
    metrics_thread.start()
    
    # Démarrer le serveur Flask
    app.run(host='0.0.0.0', port=8000)