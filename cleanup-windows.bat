@echo off
REM Script de limpieza para Windows - Ejecutar en PowerShell como Administrador

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Limpiando contenedores viejos...
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Detener TODOS los contenedores en ejecución
echo [1/4] Deteniendo todos los contenedores...
docker stop $(docker ps -q) 2>nul || echo "  (ninguno en ejecución)"

REM Remover contenedores
echo [2/4] Removiendo contenedores...
docker rm $(docker ps -a -q) 2>nul || echo "  (ninguno para remover)"

REM Mostrar estado
echo.
echo [3/4] Estado actual:
docker ps

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   AHORA SIGUE ESTOS PASOS:
echo ════════════════════════════════════════════════════════════════════════
echo.
echo 1. Cierra VS Code completamente
echo.
echo 2. En PowerShell, navega a la carpeta del proyecto:
echo    cd C:\Users\tomas\Downloads\7mo Semestre\Arquitectura\EDA-Use-Case
echo.
echo 3. Ejecuta ESTE comando (TODO EN UNA LINEA):
echo.
echo    docker compose -f .devcontainer/docker-compose.yml -f docker-compose.override.yml up -d
echo.
echo 4. ESPERA 30-40 segundos a que Kafka inicialice completamente
echo.
echo 5. Verifica con:
echo    docker ps
echo.
echo 6. Deberías ver 5 contenedores corriendo:
echo    - zookeeper
echo    - kafka
echo    - redis
echo    - backend-dev
echo    - frontend-dev
echo.
pause
