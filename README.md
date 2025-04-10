# Surveillance de Modèle d'IA

Ce projet déploie un modèle d'IA (XGBoost) dans un conteneur Docker et implémente un système de surveillance des performances (CPU, mémoire) en utilisant Prometheus et Grafana.

## Architecture

Le projet est composé de plusieurs services :

1. **Application Streamlit** : Interface utilisateur pour faire des prédictions avec le modèle
2. **Exportateur de métriques** : Serveur Flask qui collecte et expose les métriques au format Prometheus
3. **Prometheus** : Collecte et stocke les métriques de performance
4. **Grafana** : Visualise les métriques collectées par Prometheus
5. **Node Exporter** : Collecte des métriques système au niveau de l'hôte

## Démarrage

### Prérequis

- Docker et Docker Compose installés
- Placer votre modèle XGBoost (`notre_model_XGB.joblib`) et les noms des caractéristiques (`xgb_feature_names.pkl`) dans le dossier `app/`

### Lancement

```bash
docker-compose up --build -d
```

### Accès aux interfaces

- **Application Streamlit** : http://localhost:8501
- **Prometheus** : http://localhost:9090
- **Grafana** : http://localhost:3000 

## Métriques surveillées

- Utilisation CPU et mémoire
- Nombre de prédictions et temps de réponse du modèle
- Répartition des résultats des prédictions (prêts approuvés/refusés)

## Configuration de Grafana

1. Se connecter à Grafana (http://localhost:3000)
2. La source de données Prometheus et le tableau de bord sont automatiquement configurés

## Troubleshooting

Si vous rencontrez des problèmes :

1. Vérifiez les logs des conteneurs : `docker-compose logs -f [service]`
2. Assurez-vous que tous les services sont en cours d'exécution : `docker-compose ps`
3. Vérifiez la connectivité entre les conteneurs : `docker exec -it [container] ping [other_container]`