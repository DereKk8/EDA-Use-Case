"""
Configuración para conexión a servicios (Kafka, Redis).
Soporta múltiples contextos: local, dev container, Docker.
"""

import os
from typing import Dict, Any

def get_service_config() -> Dict[str, Any]:
    """
    Obtiene la configuración de servicios basada en el contexto de ejecución.
    """
    
    # Variables de entorno (si el usuario las configura)
    env_kafka = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    env_redis = os.getenv("REDIS_URL")
    
    if env_kafka and env_redis:
        # Usuario configuró variables de entorno
        return {
            "kafka_bootstrap": env_kafka,
            "redis_url": env_redis,
        }
    
    # Detectar contexto automáticamente
    # Intentar resolver 'kafka' (dentro de red Docker)
    import socket
    try:
        socket.gethostbyname("kafka")
        # ✓ Estamos en la red Docker (dev container o dentro de docker-compose)
        return {
            "kafka_bootstrap": "kafka:29092",
            "redis_url": "redis://redis:6379",
        }
    except (socket.gaierror, OSError):
        # ✗ No estamos en red Docker - intentar localhost
        return {
            "kafka_bootstrap": "localhost:9092",
            "redis_url": "redis://localhost:6379",
        }
