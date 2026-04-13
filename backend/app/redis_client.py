import json
import logging
import os

import redis as redis_lib

from app.config import get_service_config
from app.models import Notificacion, Pedido

logger = logging.getLogger(__name__)

config = get_service_config()
REDIS_URL = os.getenv("REDIS_URL", config["redis_url"])


def get_redis():
    return redis_lib.from_url(REDIS_URL, decode_responses=True)


def guardar_pedido(pedido: Pedido) -> None:
    key = f"pedido:{pedido.id}"
    get_redis().set(key, pedido.model_dump_json(), ex=3600)
    logger.info("Guardado %s", key)


def obtener_pedido(pedido_id: str) -> dict | None:
    data = get_redis().get(f"pedido:{pedido_id}")
    return json.loads(data) if data else None


def guardar_notificacion(notif: Notificacion) -> None:
    key = f"notificacion:{notif.pedido_id}"
    get_redis().set(key, notif.model_dump_json(), ex=3600)
    logger.info("Guardada %s", key)


def obtener_notificacion(pedido_id: str) -> dict | None:
    data = get_redis().get(f"notificacion:{pedido_id}")
    return json.loads(data) if data else None


def obtener_todas_notificaciones() -> list[dict]:
    """Lista todas las claves notificacion:* (SCAN, no bloquea el servidor)."""
    r = get_redis()
    out: list[dict] = []
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor=cursor, match="notificacion:*", count=100)
        for key in keys:
            data = r.get(key)
            if data:
                try:
                    out.append(json.loads(data))
                except json.JSONDecodeError:
                    logger.warning("Valor JSON inválido en %s", key)
        if cursor == 0:
            break
    out.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return out
