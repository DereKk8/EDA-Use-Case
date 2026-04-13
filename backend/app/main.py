import logging
import uuid

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.kafka_producer import publicar_pedido, start_producer, stop_producer
from app.models import Pedido, PedidoCreate, Producto
from app.redis_client import (
    guardar_pedido,
    obtener_notificacion,
    obtener_pedido,
    obtener_todas_notificaciones,
)

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_producer()
    yield
    await stop_producer()

app = FastAPI(title="Sistema de Pedidos EDA", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CATALOGO = [
    Producto(id="prod-1", nombre="Hamburguesa Clásica", precio=15000),
    Producto(id="prod-2", nombre="Pizza Margherita",    precio=22000),
    Producto(id="prod-3", nombre="Jugo Natural",        precio=5000),
    Producto(id="prod-4", nombre="Ensalada César",      precio=12000),
]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/productos")
async def listar_productos():
    return CATALOGO


@app.post("/pedidos", status_code=201)
async def crear_pedido(body: PedidoCreate):
    pedido = Pedido(
        id=str(uuid.uuid4()),
        cliente=body.cliente,
        productos=body.productos,
        total=sum(p.precio for p in body.productos),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    guardar_pedido(pedido)
    await publicar_pedido(pedido)
    return {"pedido_id": pedido.id, "estado": pedido.estado, "total": pedido.total}


@app.get("/pedidos/{pedido_id}")
async def consultar_pedido(pedido_id: str):
    pedido = obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido["notificacion"] = obtener_notificacion(pedido_id)
    return pedido


@app.get("/notificaciones")
async def listar_notificaciones():
    return obtener_todas_notificaciones()
