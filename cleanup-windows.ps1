# Script PowerShell para Windows - Limpieza de contenedores
# EJECUTAR COMO ADMINISTRADOR

Write-Host "`n"
Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  LIMPIEZA DE CONTENEDORES DOCKER" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "`n"

Write-Host "[1/3] Deteniendo todos los contenedores..." -ForegroundColor Yellow
$containers = docker ps -q
if ($containers) {
    docker stop $containers | Out-Null
    Write-Host "  ✅ Contenedores detenidos" -ForegroundColor Green
} else {
    Write-Host "  (ninguno en ejecución)" -ForegroundColor Gray
}

Write-Host "`n[2/3] Removiendo contenedores..." -ForegroundColor Yellow
$allContainers = docker ps -a -q
if ($allContainers) {
    docker rm $allContainers | Out-Null
    Write-Host "  ✅ Contenedores removidos" -ForegroundColor Green
} else {
    Write-Host "  (ninguno para remover)" -ForegroundColor Gray
}

Write-Host "`n[3/3] Estado actual:" -ForegroundColor Yellow
docker ps

Write-Host "`n"
Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  PRÓXIMOS PASOS" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n"

Write-Host "Paso 1: Cierra VS Code completamente`n" -ForegroundColor White

Write-Host "Paso 2: En esta PowerShell, navega a la carpeta del proyecto:`n" -ForegroundColor White
Write-Host "  cd C:\Users\tomas\Downloads\7mo Semestre\Arquitectura\EDA-Use-Case`n" -ForegroundColor Cyan

Write-Host "Paso 3: Ejecuta este comando (TODO EN UNA LINEA):`n" -ForegroundColor White
Write-Host "  docker compose -f .devcontainer/docker-compose.yml -f docker-compose.override.yml up -d`n" -ForegroundColor Cyan

Write-Host "Paso 4: ESPERA 30-40 segundos a que Kafka inicialice`n" -ForegroundColor Yellow

Write-Host "Paso 5: Verifica con:`n" -ForegroundColor White
Write-Host "  docker ps`n" -ForegroundColor Cyan

Write-Host "Paso 6: Deberías ver exactamente 5 contenedores corriendo:`n" -ForegroundColor White
Write-Host "  - zookeeper" -ForegroundColor Cyan
Write-Host "  - kafka" -ForegroundColor Cyan
Write-Host "  - redis" -ForegroundColor Cyan
Write-Host "  - backend-dev" -ForegroundColor Cyan
Write-Host "  - frontend-dev`n" -ForegroundColor Cyan

Write-Host "Paso 7: Abre VS Code de nuevo (Dev Container se conectará automáticamente)`n" -ForegroundColor White

Write-Host "Paso 8: En VS Code terminal, ejecuta:`n" -ForegroundColor White
Write-Host "  python diagnose.py`n" -ForegroundColor Cyan

Write-Host "Paso 9: Si ambos son ✅, ejecuta:`n" -ForegroundColor White
Write-Host "  python -m app.worker`n" -ForegroundColor Cyan

Read-Host "Presiona Enter cuando hayas completado los pasos"
