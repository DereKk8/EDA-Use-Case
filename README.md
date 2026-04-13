# Sistema de Pedidos — EDA Pattern

Sistema de pedidos de comida que implementa **Event-Driven Architecture (EDA)**.

## ¿Qué es Event-Driven Architecture?

El patrón EDA desacopla los componentes de tu aplicación con eventos asíncrónos. En este proyecto:

1. **FastAPI recibe un pedido** → lo guarda en Redis → lo publica en Kafka → responde 201 OK (en **milisegundos**)
2. **El Worker consume el evento** de Kafka **de forma independiente** → procesa el pedido → guarda una notificación en Redis

**La magia:** FastAPI nunca espera al Worker. Kafka garantiza que el evento llegue. Ambos desconocen la existencia del otro. Eso es EDA.

---

## Arquitectura del sistema

```
┌─────────────┐        ┌──────────────┐        ┌─────────────┐
│ Navegador   │──────→ │  FastAPI     │──────→ │   Redis     │
│ (Svelte)    │        │  (puerto     │        │ (pedidos)   │
└─────────────┘        │   8000)      │        └─────────────┘
                       │              │
                       │   Publica    │
                       │   evento en  │
                       │   Kafka →    │
                       └──────────────┘
                             ↓ (evento en topic "pedidos")
                       ┌──────────────────┐
                       │  Worker (Python) │
                       │  Consume evento  │
                       │  → Procesa       │
                       │  → Guarda        │
                       │    notificación  │
                       └──────────────────┘
                             ↓
                       ┌──────────────────┐
                       │  Redis           │
                       │(notificaciones)  │
                       └──────────────────┘
```

---

## Entidades de negocio

| Entidad | Descripción | Almacenamiento |
|---------|-------------|---|
| **Producto** | Ítem del menú (id, nombre, precio) | En memoria en FastAPI |
| **Pedido** | Orden de un cliente (id, cliente, productos, total, estado, created_at) | Redis con clave `pedido:{id}` |
| **Notificación** | Confirmación asíncrona del Worker via Kafka | Redis con clave `notificacion:{pedido_id}` |

---

## Stack tecnológico

| Tecnología | Versión | Rol |
|---|---|---|
| **Svelte** | 4.x | Frontend interactivo (SPA) |
| **Vite** | 5.4.11 | Bundler y servidor dev para frontend |
| **FastAPI** | latest | REST API + Kafka Producer |
| **aiokafka** | latest | Cliente Kafka asíncrono (async/await) |
| **redis-py** | latest | Cliente Redis sincrónico |
| **Redis** | 7-alpine | Persistencia de pedidos y notificaciones |
| **Apache Kafka** | Confluent latest | Message broker EDA |
| **Docker Compose** | - | Orquestación de contenedores |

---

## Despliegue (GHCR)

Este repositorio publica imágenes en GHCR automáticamente cuando hay push a la rama principal.

### Prerrequisitos

- Docker Engine o Docker Desktop
- Docker Compose v2

### 1️. Elegir el tag 

En GitHub Actions (workflow **Publish Images to GHCR**) verás tags como:

- `latest` (último commit de `main`)
- `sha-<commit>` 

### 2️. Definir imágenes y levantar el stack productivo

```bash
export BACKEND_IMAGE=ghcr.io/derekk8/eda-use-case-backend
export FRONTEND_IMAGE=ghcr.io/derekk8/eda-use-case-frontend
export IMAGE_TAG=sha-13635d7

docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

Esto levanta:

- Zookeeper
- Kafka
- Redis
- Backend (FastAPI)
- Worker (consumer Kafka)
- Frontend (Svelte servido por Nginx)

### 3️. Verificación rápida

```bash
curl http://localhost:8000/health
curl http://localhost:8000/productos
```

Frontend: http://localhost:5173

Para apagar:

```bash
docker compose -f docker-compose.prod.yml down
```

---

## Desarrollo local (solo colaboradores)

Los archivos en `.devcontainer/` y `docker-compose.override.yml` existen para desarrollo con hot reload dentro de VS Code Dev Containers. No son necesarios para evaluación ni despliegue.

### Flujo de desarrollo con Dev Container

1. Abrir el repositorio en VS Code.
2. Ejecutar `Dev Containers: Reopen in Container`.
3. Levantar servicios de desarrollo:

```bash
docker compose -f .devcontainer/docker-compose.yml -f docker-compose.override.yml up -d
```

4. En una segunda terminal, iniciar el worker manualmente:

```bash
cd /workspace && python app/worker.py
```

---

## Verificación del patrón EDA en vivo

### Opción A: Desde el navegador

1. Abre http://localhost:5173
2. Ingresa tu nombre
3. Agrega 1 o 2 productos
4. Haz clic en **"Realizar Pedido"**
5. Copia el `pedido_id` que aparece
6. En la sección "Consultar estado", pega el ID
7. Haz clic en **"Consultar"**

**Resultado esperado:**
- Primero ves: ⏳ "Procesando... (el worker aún no escribió la notificación)"
- Pasados ~2-3 segundos (refresh): ✓ "Pedido de {tu nombre} procesado correctamente"

### Opción B: Desde la línea de comandos

**Terminal 1 (si no está ya en ejecución):**
```bash
docker compose -f .devcontainer/docker-compose.yml -f docker-compose.override.yml up -d
```

**Terminal 2 (Worker):**
```bash
cd /workspace && python app/worker.py
```

**Terminal 3 (Cliente):**
```bash
# Crear un pedido
curl -s -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"cliente":"Ana","productos":[{"id":"prod-1","nombre":"Hamburguesa Clásica","precio":15000},{"id":"prod-3","nombre":"Jugo Natural","precio":5000}]}' | python3 -m json.tool

# Copiar el "pedido_id" del resultado
# Esperaremos 3 segundos para que el Worker procese el evento
sleep 3

# Verificar que ambas claves existen en Redis
docker exec -it $(docker ps --filter name=redis -q) redis-cli KEYS "*"
# → Resultado:
#   1) "pedido:XXXXXXX-XXXX-..."
#   2) "notificacion:XXXXXXX-XXXX-..."  ← El Worker escribió esto

# Leer la notificación generada por el Worker
docker exec -it $(docker ps --filter name=redis -q) redis-cli GET "notificacion:XXXXXXX-XXXX-..."
# → {"pedido_id":"...","mensaje":"Pedido de Ana procesado correctamente",...}

# Consultar via API (retorna pedido + notificación juntos)
curl -s http://localhost:8000/pedidos/XXXXXXX-XXXX-... | python3 -m json.tool
# → {"id":"XXXXXXX-XXXX-...","cliente":"Ana","productos":[...],"notificacion":{...}}
```

**En Terminal 2 (Worker) verás:**
```
Worker iniciado, escuchando topic 'pedidos'...
Notificacion guardada para pedido XXXXXXX-XXXX-...
```

---

## Para la presentación en vivo

**Abre 2 terminales simultáneamente:**

### Terminal IZQUIERDA: Worker escuchando

```bash
# TERMINAL 1: Producción de eventos
cd /workspace && python app/worker.py

# Verás:
# Worker iniciado, escuchando topic 'pedidos'...
# ← Ahora espera... (no hace nada hasta recibir un evento)
```

### Terminal DERECHA: Cliente creando pedidos

```bash
# TERMINAL 2: Consumidor (cliente)
# Crea un pedido
curl -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"cliente":"Presentacion EDA","productos":[{"id":"prod-1","nombre":"Hamburguesa Clásica","precio":15000}]}'

# ← Respuesta INMEDIATA en milisegundos con pedido_id
# {"pedido_id":"xxxx-xxxx-xxxx","estado":"pendiente","total":15000}

# ← En TERMINAL 1 (Worker) aparece casi instantáneamente:
# Notificacion guardada para pedido xxxx-xxxx-xxxx
```

**Frase para la presentación:**

> "FastAPI publicó el evento y respondió en **milisegundos**, sin saber que el Worker existe. 
> El Worker procesó el evento de forma **independiente**, sin saber que FastAPI existe. 
> Kafka garantizó la entrega entre ambos. 
> Eso es **Event-Driven Architecture**."

---

## Estructura del código

```
/workspace/
├── app/                          ← Paquete Python para FastAPI
│   ├── __init__.py               ← Marca como paquete Python
│   ├── models.py                 ← Entidades Pydantic (Producto, Pedido, Notificación)
│   ├── main.py                   ← FastAPI app + endpoints REST
│   ├── redis_client.py           ← Funciones para guardar/leer de Redis
│   ├── kafka_producer.py         ← Iniciar producer de Kafka, publicar eventos
│   └── worker.py                 ← Consumer de Kafka (motor EDA)
│
├── frontend/
│   ├── package.json              ← Scripts y dependencias Node
│   ├── Dockerfile                ← Imagen productiva del frontend
│   ├── nginx.conf                ← Configuración SPA en Nginx
│   ├── vite.config.js            ← Configuración Vite + Svelte
│   ├── index.html                ← HTML root
│   └── src/
│       ├── main.js               ← Entry point JS → monta App.svelte
│       └── App.svelte            ← Componente root (catálogo + carrito + consultas)
│
├── backend/
│   ├── requirements.txt           ← Dependencias Python
│   └── Dockerfile                 ← Imagen productiva backend/worker
│
├── .devcontainer/
│   ├── devcontainer.json         ← Configuración VS Code Dev Container
│   └── docker-compose.yml        ← Compose base para entorno de colaboración
│
├── .github/
│   └── workflows/
│       └── publish-ghcr.yml      ← CI/CD para publicar imágenes en GHCR
├── docker-compose.override.yml   ← Override de desarrollo (Dev Containers)
├── docker-compose.prod.yml       ← Orquestación productiva desde imágenes GHCR
├── .dockerignore                 ← Exclusiones para build de imágenes
└── README.md                     ← Este archivo
```

---

## Instalación manual de dependencias (sólo si no usas Dev Container)

```bash
# Python
cd /workspace
pip install fastapi uvicorn aiokafka redis pydantic

# Node/Svelte
cd /workspace/frontend
npm install
```

---

## Troubleshooting

### "Cannot connect to Kafka"
- Kafka tarda ~20-30 segundos en inicializar. Espera antes de crear pedidos.
- Verifica que `docker ps` muestra el contenedor `kafka` en state `Up`.

### "Connection refused on localhost:5173"
- El override puede tardar en compilar el frontend. Espera 10 segundos después de `up -d`.
- Abre http://localhost:5173 en el navegador.

### "Redis connection error"
- Verifica: `docker exec -it $(docker ps --filter name=redis -q) redis-cli PING`
- Debe responder `PONG`.

### El Worker no muestra "Notificacion guardada..."
- ¿Ejecutaste el Worker? Revisa que el comando `python app/worker.py` está corriendo en una terminal.
- ¿El backend respondió con un `pedido_id`? Si no, hay error en FastAPI (revisa logs con `docker logs ...`).
- ¿Esperaste ~2-3 segundos después de crear el pedido?

### Hot reload no funciona en frontend
- Vite debería compilar en ~500ms. Si no ves cambios, revisa:
  - ¿El contenedor `frontend-dev` está en `Up`? (`docker ps`)
  - ¿Los logs de Vite muestran cambios? (`docker logs frontend-dev`)

---

## Lecciones de arquitectura

1. **Desacoplamiento:** FastAPI no conoce al Worker. El Worker no conoce a FastAPI.
2. **Asincronía:** Kafka garantiza que el evento llegará, aunque el Worker esté caído momentáneamente.
3. **Escalabilidad:** Puedes agregar más Workers sin tocar FastAPI.
4. **Resiliencia:** Si FastAPI cae, los eventos estarán en Kafka. Si el Worker cae, los eventos se almacenan.

---

## Licencia

Este es un proyecto de **demostración educativa** para entender EDA. Usa libremente.

¡Diviértete aprendiendo arquitectura orientada a eventos!

