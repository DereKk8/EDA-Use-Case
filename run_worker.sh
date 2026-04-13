#!/bin/bash
# Script para ejecutar el Worker correctamente

cd /workspace

echo "═══════════════════════════════════════════════════════════════════"
echo "  SISTEMA DE PEDIDOS EDA - WORKER"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  IMPORTANTE:"
echo "  Asegúrate de que la infraestructura (Kafka, Redis) está corriendo:"
echo "  docker compose -f .devcontainer/docker-compose.yml \\"
echo "     -f docker-compose.override.yml up -d"
echo ""
echo "  Esperando 5 segundos..."
sleep 5

echo ""
echo "🚀 Iniciando Worker..."
echo ""

python -m app.worker
