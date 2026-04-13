import asyncio, os, json, logging
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer
from app.models import Notificacion
from app.redis_client import guardar_notificacion
from app.config import get_service_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

# Detectar contexto automáticamente (docker, dev container, localhost)
config = get_service_config()
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", config["kafka_bootstrap"])

async def main():
    consumer = AIOKafkaConsumer(
        "pedidos",
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id="worker-group",
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    await consumer.start()
    logger.info("Worker iniciado, escuchando topic 'pedidos'...")
    try:
        async for msg in consumer:
            data = msg.value
            pedido_id = data.get("id")
            cliente   = data.get("cliente", "desconocido")
            try:
                notif = Notificacion(
                    pedido_id=pedido_id,
                    mensaje=f"Pedido de {cliente} procesado correctamente",
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
                guardar_notificacion(notif)
                logger.info(f"Notificacion guardada para pedido {pedido_id}")
            except Exception as e:
                logger.error(f"Error procesando pedido {pedido_id}: {e}")
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())
