import asyncio
import json
import logging
import os

from datetime import datetime, timezone

from aiokafka import AIOKafkaConsumer

from app.config import get_kafka_topic, get_service_config
from app.models import Notificacion
from app.redis_client import guardar_notificacion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

config = get_service_config()
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", config["kafka_bootstrap"])
KAFKA_TOPIC = get_kafka_topic()

async def main():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id="worker-group",
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    await consumer.start()
    logger.info("Worker iniciado, escuchando topic '%s'...", KAFKA_TOPIC)
    try:
        async for msg in consumer:
            data = msg.value
            pedido_id = data.get("id")
            cliente = data.get("cliente", "desconocido")
            try:
                notif = Notificacion(
                    pedido_id=pedido_id,
                    mensaje=f"Pedido de {cliente} procesado correctamente",
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
                guardar_notificacion(notif)
                logger.info("Notificacion guardada para pedido %s", pedido_id)
            except Exception as e:
                logger.error("Error procesando pedido %s: %s", pedido_id, e)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())
