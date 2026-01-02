# Guía de Desarrollo - DIVIPOLA API

## 🚀 Inicio Rápido para Desarrollo

### Opción 1: Script Automático
```bash
./dev.sh
```

### Opción 2: Comandos Manuales

#### Iniciar entorno de desarrollo
```bash
docker-compose -f docker-compose.dev.yml up
```

#### Iniciar en segundo plano
```bash
docker-compose -f docker-compose.dev.yml up -d
```

#### Ver logs en tiempo real
```bash
docker-compose -f docker-compose.dev.yml logs -f api
```

#### Detener servicios
```bash
docker-compose -f docker-compose.dev.yml down
```

## ✨ Características del Modo Desarrollo

- ✅ **Hot Reload Automático**: Los cambios en el código se reflejan automáticamente
- ✅ **Volúmenes Montados**: El código se sincroniza en tiempo real
- ✅ **Logs Detallados**: Ver todos los logs en tiempo real
- ✅ **Debugging**: Herramientas de debug incluidas (ipython, ipdb)
- ✅ **Entorno Aislado**: Base de datos y Redis separados del entorno de producción

## 📝 Flujo de Trabajo

1. **Inicia el entorno de desarrollo:**
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

2. **Haz cambios en tu código** - El servidor se reiniciará automáticamente

3. **Verifica los cambios** en http://localhost:8000/docs

4. **Revisa los logs** si hay errores:
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f api
   ```

## 🔧 Comandos Útiles

### Reconstruir imagen después de cambios en requirements.txt
```bash
docker-compose -f docker-compose.dev.yml build --no-cache api
docker-compose -f docker-compose.dev.yml up -d
```

### Ejecutar comandos dentro del contenedor
```bash
docker-compose -f docker-compose.dev.yml exec api bash
```

### Ejecutar script de recolección de datos
```bash
docker-compose -f docker-compose.dev.yml exec api python -m scripts.collect_data
```

### Limpiar todo (volúmenes incluidos)
```bash
docker-compose -f docker-compose.dev.yml down -v
```

## 🐛 Troubleshooting

### El hot-reload no funciona
- Verifica que el volumen esté montado correctamente
- Asegúrate de que los archivos `.py` estén siendo monitoreados
- Revisa los logs: `docker-compose -f docker-compose.dev.yml logs api`

### Cambios en requirements.txt no se aplican
- Reconstruye la imagen: `docker-compose -f docker-compose.dev.yml build --no-cache api`
- Reinicia el servicio: `docker-compose -f docker-compose.dev.yml restart api`

### Puerto 8000 ya está en uso
- Cambia el puerto en `docker-compose.dev.yml`:
  ```yaml
  ports:
    - "8001:8000"  # Usa 8001 en lugar de 8000
  ```

## 📊 Diferencias entre Desarrollo y Producción

| Característica | Desarrollo | Producción |
|---------------|------------|------------|
| Hot Reload | ✅ Sí | ❌ No |
| Volúmenes | ✅ Montados | ❌ No |
| Logs | ✅ Detallados | ⚠️ Optimizados |
| Debugging | ✅ Habilitado | ❌ Deshabilitado |
| Volúmenes DB | `postgres_dev_data` | `postgres_data` |

