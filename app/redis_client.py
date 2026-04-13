import os, json, logging
import redis as redis_lib
from app.models import Pedido, Notificacion
from app.config import get_service_config

logger = logging.getLogger(__name__)

# Detectar contexto automáticamente (docker, dev container, localhost)
config = get_service_config()
REDIS_URL = os.getenv("REDIS_URL", config["redis_url"])

def get_redis():
    return redis_lib.from_url(REDIS_URL, decode_responses=True)

def guardar_pedido(pedido: Pedido) -> None:
    get_redis().set(f"pedido:{pedido.id}", pedido.model_dump_json(), ex=3600)
    logger.info(f"Guardado pedido:{pedido.id}")

def obtener_pedido(pedido_id: str) -> dict | None:
    data = get_redis().get(f"pedido:{pedido_id}")
    return json.loads(data) if data else None

def guardar_notificacion(notif: Notificacion) -> None:
    get_redis().set(f"notificacion:{notif.pedido_id}", notif.model_dump_json(), ex=3600)
    logger.info(f"Guardada notificacion:{notif.pedido_id}")

def obtener_notificacion(pedido_id: str) -> dict | None:
    data = get_redis().get(f"notificacion:{pedido_id}")
    return json.loads(data) if data else None
