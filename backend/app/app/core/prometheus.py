# -*- coding: utf-8 -*-
"""
Configuration de Prometheus pour le monitoring de l'application.
"""
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_client import Counter, Histogram
import time

# Métriques personnalisées
llm_request_counter = Counter(
    "llm_requests_total", 
    "Total number of requests to LLM services",
    ["model", "status"]
)

llm_request_duration = Histogram(
    "llm_request_duration_seconds",
    "Duration of LLM requests in seconds",
    ["model"]
)

db_query_duration = Histogram(
    "db_query_duration_seconds",
    "Duration of database queries in seconds",
    ["operation"]
)

# Classe pour mesurer le temps d'exécution
class TimerContextManager:
    def __init__(self, histogram, labels=None):
        self.histogram = histogram
        self.labels = labels or {}
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.histogram.labels(**self.labels).observe(duration)

# Fonction pour initialiser l'instrumentator Prometheus
def setup_prometheus_instrumentator():
    instrumentator = Instrumentator()
    
    # Ajouter des métriques par défaut
    instrumentator.add(metrics.latency())
    instrumentator.add(metrics.requests())
    # Supprimez ces lignes car ces métriques n'existent pas
    # instrumentator.add(metrics.requests_in_progress())
    # instrumentator.add(metrics.dependency_requests())
    # instrumentator.add(metrics.dependency_latency())
    
    return instrumentator