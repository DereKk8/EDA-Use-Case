# EDA Orders Demo

Aplicación de pedidos de comida basada en Event-Driven Architecture (EDA):

- FastAPI recibe pedidos y publica eventos en Kafka.
- Worker consume eventos y escribe notificaciones.
- Redis almacena pedidos y notificaciones.
- Frontend (Svelte + Nginx) consume la API.

## Deploy público con GHCR

El flujo recomendado para usuarios externos es desplegar imágenes preconstruidas desde GHCR usando [docker-compose.prod.yml](docker-compose.prod.yml).

### Requisitos

- Docker Engine / Docker Desktop
- Docker Compose v2

### 1. Definir imágenes y tag

```bash
export BACKEND_IMAGE=ghcr.io/<owner>/<repo-backend>
export FRONTEND_IMAGE=ghcr.io/<owner>/<repo-frontend>
export IMAGE_TAG=latest
```

Opcional: usa un tag inmutable tipo `sha-<commit>` para despliegues reproducibles.

### 2. Levantar el stack

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

Servicios incluidos:

- zookeeper
- kafka
- redis
- backend
- worker
- frontend

### 3. Verificación rápida

```bash
curl http://localhost:8000/health
curl http://localhost:8000/productos
```

Frontend: http://localhost:5173

### 4. Apagar

```bash
docker compose -f docker-compose.prod.yml down
```

## Prueba EDA en 30 segundos

```bash
curl -s -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"cliente":"Ana","productos":[{"id":"prod-1","nombre":"Hamburguesa Clásica","precio":15000}]}'
```

Luego consulta el pedido con el `pedido_id` retornado:

```bash
curl -s http://localhost:8000/pedidos/<pedido_id>
```

## Desarrollo (solo contribuidores)

La documentación de desarrollo local se mantiene aparte para no mezclar el flujo público de despliegue:

- Linux/macOS: [SETUP.md](SETUP.md)

## Estructura mínima

- [backend/app/main.py](backend/app/main.py): API FastAPI
- [backend/app/worker.py](backend/app/worker.py): consumidor Kafka
- [backend/app/kafka_producer.py](backend/app/kafka_producer.py): productor Kafka
- [backend/app/redis_client.py](backend/app/redis_client.py): acceso Redis
- [frontend/src/App.svelte](frontend/src/App.svelte): UI
- [docker-compose.prod.yml](docker-compose.prod.yml): despliegue productivo

