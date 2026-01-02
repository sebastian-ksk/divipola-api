# Comandos para ejecutar el proyecto DIVIPOLA API

## Opción 1: Desarrollo Local con Docker Compose (Hot Reload)

### 1. Levantar servicios en modo desarrollo
```bash
docker-compose -f docker-compose.dev.yml up
```

### 2. Levantar en segundo plano
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Ver logs en tiempo real
```bash
docker-compose -f docker-compose.dev.yml logs -f api
```

### 4. Detener servicios
```bash
docker-compose -f docker-compose.dev.yml down
```

### 5. Reconstruir imagen de desarrollo
```bash
docker-compose -f docker-compose.dev.yml build --no-cache
```

**Características del modo desarrollo:**
- ✅ Hot reload automático al detectar cambios
- ✅ Volúmenes montados para sincronización en tiempo real
- ✅ Logs detallados
- ✅ Herramientas de debugging incluidas

---

## Opción 2: Producción con Docker Compose

### 1. Levantar todos los servicios (PostgreSQL, Redis, API)
```bash
docker-compose up -d
```

### 2. Ver logs de los servicios
```bash
docker-compose logs -f
```

### 3. Recolectar datos iniciales
```bash
docker-compose exec api python -m scripts.collect_data
```

### 4. Verificar que la API está funcionando
```bash
curl http://localhost:8000/health
```

### 5. Acceder a la documentación de la API
Abrir en el navegador: http://localhost:8000/docs

### 6. Detener los servicios
```bash
docker-compose down
```

### 7. Detener y eliminar volúmenes (limpiar todo)
```bash
docker-compose down -v
```

---

## Opción 3: Instalación local (sin Docker)

### 1. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crear archivo `.env`:
```env
DATABASE_URL=postgresql://divipola_user:divipola_pass@localhost:5432/divipola_db
REDIS_URL=redis://localhost:6379/0
```

### 4. Asegurar que PostgreSQL y Redis estén corriendo
```bash
# PostgreSQL debe estar en puerto 5432
# Redis debe estar en puerto 6379
```

### 5. Recolectar datos
```bash
python -m scripts.collect_data
```

### 6. Ejecutar la API
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Comandos útiles

### Reconstruir la imagen de Docker
```bash
docker-compose build --no-cache
```

### Ejecutar comandos dentro del contenedor
```bash
docker-compose exec api bash
```

### Ver logs solo de la API
```bash
docker-compose logs -f api
```

### Reiniciar un servicio específico
```bash
docker-compose restart api
```

