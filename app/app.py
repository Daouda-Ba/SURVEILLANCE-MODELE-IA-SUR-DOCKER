import streamlit as st
import joblib
import pandas as pd
import numpy as np
import time
import os
import requests


METRICS_EXPORTER_URL = "http://metrics_exporter:8000"

# Fonction pour envoyer des metriques a l'exportateur
def send_metric(metric_name, value, labels=None):
    try:
        payload = {
            "name": metric_name,
            "value": value,
            "labels": labels or {}
        }
        requests.post(f"{METRICS_EXPORTER_URL}/update", json=payload, timeout=0.5)
    except Exception as e:
        # Ignorer les erreurs de connexion
        pass

# Chargement de modèle et des features
@st.cache_resource
def load_model():
    try:
        model = joblib.load("/app/notre_model_XGB.joblib")
        feature_names = joblib.load("/app/xgb_feature_names.pkl")
        return model, feature_names
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle ou des features : {e}")
        return None, None

model, feature_names = load_model()

# Interface utilisateur
st.title("🔍 Prédiction du Risque de Crédit")
st.write("Entrez les caractéristiques du client pour obtenir une évaluation.")

# Champs de saisie des features
person_age = st.number_input("Âge du client", min_value=18, max_value=100, value=30)
person_income = st.number_input("Revenu mensuel (€)", min_value=0, value=5000)
person_emp_length = st.number_input("Durée d'emploi (années)", min_value=0.0, value=5.0)
loan_amnt = st.number_input("Montant du prêt (€)", min_value=500, value=10000)
loan_int_rate = st.number_input("Taux d'intérêt du prêt (%)", min_value=0.0, max_value=50.0, value=10.0)
loan_percent_income = st.number_input("Pourcentage du revenu dédié au prêt", min_value=0.0, max_value=1.0, value=0.2)
cb_person_cred_hist_length = st.number_input("Longueur de l'historique de crédit", min_value=1, max_value=30, value=5)

# Variables categoriques
person_home_ownership = st.selectbox("Type de propriété", ["OWN", "RENT", "MORTGAGE", "OTHER"])
loan_intent = st.selectbox("Intention du prêt", ["EDUCATION", "MEDICAL", "VENTURE", "PERSONAL", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"])
loan_grade = st.selectbox("Grade du prêt", ["A", "B", "C", "D", "E", "F", "G"])
cb_person_default_on_file = st.selectbox("Historique de défaut de paiement", ["Y", "N"])

# Prédiction
if st.button("🔮 Prédire le risque de crédit"):
    # Envoyer une métrique pour indiquer qu'une prédiction a été demandé
    send_metric("prediction_requests_total", 1)
    
    # Mesurer le temps de prediction
    start_time = time.time()
    
    # Création du DataFrame utilisateur
    data = pd.DataFrame([[
        person_age, person_income, person_emp_length, loan_amnt,
        loan_int_rate, loan_percent_income, cb_person_cred_hist_length,
        person_home_ownership, loan_intent, loan_grade, cb_person_default_on_file
    ]], columns=[
        "person_age", "person_income", "person_emp_length", "loan_amnt", 
        "loan_int_rate", "loan_percent_income", "cb_person_cred_hist_length",
        "person_home_ownership", "loan_intent", "loan_grade", "cb_person_default_on_file"
    ])
    
    # Encodage one-hot comme lors de l'entraînement
    data = pd.get_dummies(data)
    
    # Ajouter les colonnes manquantes avec des 0
    for col in feature_names:
        if col not in data.columns:
            data[col] = 0
    
    # Réorganiser les colonnes 
    data = data[feature_names]
    
    try:
        # Faire la prédiction avec le modèle
        prediction = model.predict(data)[0]
        
        # Enregistrer le temps de prédiction
        prediction_time = time.time() - start_time
        
        # Envoyer des métriques sur le temps de prédiction
        send_metric("model_prediction_latency_seconds", prediction_time)
        
        # Envoyer des métriques sur le résultat de la prédiction
        result = "approved" if prediction == 1 else "rejected"
        send_metric("model_prediction_results", 1, {"result": result})
        
        # Afficher le résultat
        if prediction == 1:
            st.success("✅ **Prêt Approuvé !**")
        else:
            st.error("❌ **Prêt Refusé !**")
    
    except Exception as e:
        # Envoyer des métriques sur les erreurs
        send_metric("model_prediction_errors", 1)
        st.error(f"Erreur lors de la prédiction : {e}")