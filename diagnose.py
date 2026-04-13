#!/usr/bin/env python
"""
Script de diagnóstico para verificar conectividad con Kafka y Redis.
"""

import sys
import socket
from app.config import get_service_config

def test_connection(host: str, port: int, timeout: float = 2.0) -> bool:
    """Probar conexión TCP a un host:puerto."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    except Exception as e:
        return False
    finally:
        sock.close()

def main():
    print("\n" + "="*70)
    print("  🔧 DIAGNÓSTICO EDA - Verificación de conectividad")
    print("="*70 + "\n")
    
    config = get_service_config()
    kafka_bootstrap = config["kafka_bootstrap"]
    redis_url = config["redis_url"]
    
    print(f"📍 Configuración detectada:")
    print(f"   Kafka: {kafka_bootstrap}")
    print(f"   Redis: {redis_url}")
    print()
    
    # Extraer host y puerto de Kafka
    kafka_host, kafka_port = kafka_bootstrap.rsplit(":", 1)
    kafka_port = int(kafka_port)
    
    # Extraer host y puerto de Redis
    redis_parts = redis_url.replace("redis://", "").rsplit(":", 1)
    redis_host = redis_parts[0]
    redis_port = int(redis_parts[1])
    
    print("🧪 Probando conexiones...")
    print()
    
    # Test Kafka
    kafka_ok = test_connection(kafka_host, kafka_port)
    kafka_status = "✅ OK" if kafka_ok else "❌ FALLA"
    print(f"   Kafka ({kafka_host}:{kafka_port}): {kafka_status}")
    
    # Test Redis
    redis_ok = test_connection(redis_host, redis_port)
    redis_status = "✅ OK" if redis_ok else "❌ FALLA"
    print(f"   Redis ({redis_host}:{redis_port}): {redis_status}")
    
    print()
    print("="*70)
    
    if kafka_ok and redis_ok:
        print("  ✅ LISTO - Todos los servicios están accesibles")
        print()
        print("  Puedes ejecutar:")
        print("    python -m app.worker")
        print()
        return 0
    else:
        print("  ❌ ERRORES DETECTADOS")
        if not kafka_ok:
            print()
            print("  ⚠️  Kafka no accesible. Verifica que:")
            print("     1. Ejecutaste en HOST: docker compose -f .devcontainer/docker-compose.yml \\")
            print("        -f docker-compose.override.yml up -d")
            print("     2. Esperaste 30 segundos a que Kafka inicialice")
            print("     3. Kafka está escuchando en " + kafka_bootstrap)
        if not redis_ok:
            print()
            print("  ⚠️  Redis no accesible. Verifica que:")
            print("     1. Ejecutaste en HOST: docker compose -f .devcontainer/docker-compose.yml \\")
            print("        -f docker-compose.override.yml up -d")
            print("     2. Redis está escuchando en " + redis_url)
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
