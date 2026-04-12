# EDA-Use-Case

## Inicio rapido

Este proyecto esta configurado para ejecutarse completamente dentro de un Development Container de VS Code.
No necesitas tener Python, Node.js, Kafka ni Redis instalados en tu maquina host.

### 1. Prerrequisitos en host

- Docker Desktop (or Docker Engine) with Compose support
- Visual Studio Code
- VS Code Dev Containers extension

### 2. Abrir en contenedor

1. Abre este repositorio en VS Code.
2. Ejecuta la paleta de comandos -> `Dev Containers: Reopen in Container`.
3. Espera a que el contenedor termine de construirse y finalice `postCreateCommand`:
	- Dependencias de Python desde `backend/requirements.txt`
	- Dependencias de Node en `frontend/`

VS Code se conectara al servicio `backend-dev` como entorno principal de desarrollo.

### 3. Levantar servicios de infraestructura

Desde una terminal dentro del contenedor (o en host), levanta el stack de eventos:

```bash
docker compose -f .devcontainer/docker-compose.yml up -d zookeeper kafka redis
```

Servicios y endpoints:

- Zookeeper: `localhost:2181`
- Kafka (herramientas en host): `localhost:9092`
- Kafka (dentro de la red Docker): `kafka:29092`
- Redis: `redis:6379`

### 4. Ejecutar servicios de aplicacion

Backend (FastAPI):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (Svelte + Vite):

```bash
npm --prefix frontend run dev
```

Puertos de desarrollo reenviados:

- Frontend: `5173`
- API Backend: `8000`

### 5. Override opcional de autoarranque

Si quieres comportamiento de autoarranque, usa el archivo override incluido en el repositorio:

- `docker-compose.override.yml` inicia el backend con hot reload
- Tambien define un servicio `frontend-dev` para autoarrancar Vite

Puedes levantarlo con:

```bash
docker compose -f .devcontainer/docker-compose.yml -f docker-compose.override.yml up -d
```

## Verificaciones rapidas

Ejecuta esto dentro del contenedor `backend-dev`:

```bash
python --version
pip --version
```

```bash
python - <<'PY'
import socket
print('kafka:', socket.gethostbyname('kafka'))
print('redis:', socket.gethostbyname('redis'))
PY
```
