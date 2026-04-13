# Setup para contribuidores (Linux/macOS)

Este documento es solo para desarrollo local. Para despliegue público usa [README.md](README.md).

## Requisitos

- Docker + Docker Compose v2
- (Opcional) VS Code + Dev Containers

## Levantar entorno de desarrollo

```bash
docker compose -f .devcontainer/docker-compose.yml -f docker-compose.override.yml up -d
```

Verifica estado:

```bash
docker ps
```

## Iniciar worker manualmente

```bash
cd backend
python -m app.worker
```

## Diagnóstico rápido

```bash
python diagnose.py
```

## Apagar entorno de desarrollo

```bash
docker compose -f .devcontainer/docker-compose.yml -f docker-compose.override.yml down
```
