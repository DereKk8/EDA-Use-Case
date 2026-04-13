import json
import logging
import os

from aiokafka import AIOKafkaProducer

from app.config import get_kafka_topic, get_service_config
from app.models import Pedido

logger = logging.getLogger(__name__)

config = get_service_config()
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", config["kafka_bootstrap"])
KAFKA_TOPIC = get_kafka_topic()

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
    await producer.send_and_wait(KAFKA_TOPIC, value=pedido.model_dump())
    logger.info("Evento publicado para pedido %s", pedido.id)
