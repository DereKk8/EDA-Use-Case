import os, json, logging
from aiokafka import AIOKafkaProducer
from app.models import Pedido
from app.config import get_service_config

logger = logging.getLogger(__name__)

# Detectar contexto automáticamente (docker, dev container, localhost)
config = get_service_config()
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", config["kafka_bootstrap"])

producer: AIOKafkaProducer | None = None

async def start_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()
    logger.info("Kafka producer iniciado")

async def stop_producer():
    global producer
    if producer:
        await producer.stop()

async def publicar_pedido(pedido: Pedido) -> None:
    if not producer:
        raise RuntimeError("Producer no inicializado")
    await producer.send_and_wait("pedidos", value=pedido.model_dump())
    logger.info(f"Evento publicado para pedido {pedido.id}")
