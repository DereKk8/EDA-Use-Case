from pydantic import BaseModel
from typing import List

class Producto(BaseModel):
    id: str
    nombre: str
    precio: float

class PedidoCreate(BaseModel):
    cliente: str
    productos: List[Producto]

class Pedido(BaseModel):
    id: str
    cliente: str
    productos: List[Producto]
    total: float
    estado: str = "pendiente"
    created_at: str

class Notificacion(BaseModel):
    pedido_id: str
    mensaje: str
    estado: str = "procesado"
    created_at: str
