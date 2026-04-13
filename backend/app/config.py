import os
import socket


DEFAULT_KAFKA_BOOTSTRAP = "localhost:9092"
DEFAULT_REDIS_URL = "redis://localhost:6379"
DOCKER_KAFKA_BOOTSTRAP = "kafka:29092"
DOCKER_REDIS_URL = "redis://redis:6379"
DEFAULT_PEDIDOS_TOPIC = "pedidos"


def _running_in_docker_network() -> bool:
    try:
        socket.gethostbyname("kafka")
        return True
    except (socket.gaierror, OSError):
        return False


def get_service_config() -> dict[str, str]:
    """Obtiene la configuración de Kafka y Redis según el contexto de ejecución."""

    env_kafka = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    env_redis = os.getenv("REDIS_URL")

    if env_kafka and env_redis:
        return {
            "kafka_bootstrap": env_kafka,
            "redis_url": env_redis,
        }

    if _running_in_docker_network():
        return {
            "kafka_bootstrap": DOCKER_KAFKA_BOOTSTRAP,
            "redis_url": DOCKER_REDIS_URL,
        }

    return {
        "kafka_bootstrap": DEFAULT_KAFKA_BOOTSTRAP,
        "redis_url": DEFAULT_REDIS_URL,
    }


def get_kafka_topic() -> str:
    return os.getenv("KAFKA_TOPIC_PEDIDOS", DEFAULT_PEDIDOS_TOPIC)
