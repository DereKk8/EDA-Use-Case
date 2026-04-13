# SETUP EDA en Windows

## 🚨 Tu Problema Actual

Tienes **contenedores duplicados y Kafka no está corriendo**.

```
docker ps muestra:
  ✅ devcontainer-redis-1
  ✅ devcontainer-zookeeper-1  
  ✅ eda-use-case_devcontainer-backend-dev-1
  ❌ Kafka NO APARECE
```

## ✅ Solución

### Paso 1 — Limpiar todo

Abre **PowerShell COMO ADMINISTRADOR** y ejecuta:

```powershell
# Detener todos
docker stop $(docker ps -q)

# Remover todos
docker rm $(docker ps -a -q)

# Verificar (debe estar vacío)
docker ps
```

### Paso 2 — Navegar a la carpeta

```powershell
cd "C:\Users\tomas\Downloads\7mo Semestre\Arquitectura\EDA-Use-Case"
```

(Nota: usa comillas porque la ruta tiene espacios)

### Paso 3 — Levantar TODO de nuevo

```powershell
docker compose -f .devcontainer/docker-compose.yml -f docker-compose.override.yml up -d
```

⏱️ **ESPERA 30-40 segundos** (Kafka tarda!!)

### Paso 4 — Verificar

```powershell
docker ps
```

**Debes ver EXACTAMENTE estos 5 contenedores:**

```
zookeeper                  Up 2 minutes
kafka                      Up 2 minutes   ← ⭐ CRÍTICO: DEBE ESTAR AQUÍ
redis                      Up 2 minutes
backend-dev                Up 2 minutes
frontend-dev               Up 2 minutes
```

Si **Kafka no aparece**, espera 10 más y repite `docker ps`.

### Paso 5 — Abrir VS Code

1. **Cierra VS Code completamente**
2. **Abre VS Code de nuevo**
3. Paleta: `Ctrl+Shift+P`
4. `Dev Containers: Reopen in Container`
5. Espera a que se conecte

### Paso 6 — Verificar conectividad (en VS Code terminal)

```bash
python diagnose.py
```

**Esperado:**
```
✅ Kafka (localhost:9092): ✅ OK
✅ Redis (localhost:6379): ✅ OK
```

### Paso 7 — Ejecutar el Worker

```bash
python -m app.worker
```

**Esperado:**
```
Worker iniciado, escuchando topic 'pedidos'...
```

---

## 🔍 Si algo falla

### ❌ Kafka no aparece en `docker ps`

**Causa:** El containedor falló al iniciar

**Solución:**
```powershell
docker compose -f .devcontainer/docker-compose.yml -f docker-compose.override.yml logs kafka
```

Esto mostrará el error. Comparte el output si necesitas ayuda.

### ❌ Redis no responde

**Verifica que esté escuchando:**
```powershell
docker ps | findstr redis
```

Debería mostrar:
```
0.0.0.0:6379->6379/tcp
```

### ❌ "Dev Container not found"

**Solución:**
```powershell
# Dentro de la carpeta del proyecto:
code .
# Paleta: "Dev Containers: Reopen in Container"
```

---

## 📋 Checklist Final

- [ ] `docker ps` muestra 5 contenedores (incluyendo Kafka)
- [ ] `python diagnose.py` muestra ✅ en ambos
- [ ] `python -m app.worker` dice "Worker iniciado..."
- [ ] Puedes visitar `http://localhost:5173` en navegador
- [ ] Puedes visitar `http://localhost:8000/health` en navegador

---

## 🎬 Para la presentación

**Terminal 1 (PowerShell):**
```powershell
docker compose -f .devcontainer/docker-compose.yml -f docker-compose.override.yml logs -f
```

**Terminal 2 (VS Code):**
```bash
python -m app.worker
```

**Terminal 3 (PowerShell):**
```powershell
curl http://localhost:8000/pedidos -Method POST -Body @{cliente="test"} | ConvertTo-Json
```

---

¿Problemas? Cuéntame el output exacto de `docker ps`.
