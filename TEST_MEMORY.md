# 🧪 Guía de Pruebas de Manejo de Memoria

## Pruebas Automáticas

### Ejecutar el script de prueba:
```bash
cd backend
python3 test_memory.py
```

Este script:
- Verifica estadísticas de caché antes y después
- Hace múltiples requests para llenar los cachés
- Verifica que los límites funcionen
- Limpia los cachés y muestra el resultado

## Pruebas Manuales

### 1. Ver Estadísticas de Caché

**Con curl:**
```bash
curl http://localhost:8080/cache/stats | jq
```

**En el navegador:**
```
http://localhost:8080/cache/stats
```

**Respuesta esperada:**
```json
{
  "cache_stats": {
    "schema_cache_size": 1,
    "schema_cache_max": 50,
    "dimensions_cache_size": 1,
    "dimensions_not_found_cache_size": 0,
    "dimensions_not_found_cache_max": 100
  },
  "metrics_stats": {
    "total_metrics": 5,
    "max_metrics": 1000
  }
}
```

### 2. Limpiar Todos los Cachés

**Con curl:**
```bash
curl -X POST http://localhost:8080/cache/clear | jq
```

**Con Python requests:**
```python
import requests
response = requests.post("http://localhost:8080/cache/clear")
print(response.json())
```

**Respuesta esperada:**
```json
{
  "status": "success",
  "message": "Todos los cachés han sido limpiados",
  "cache_stats": {
    "schema_cache_size": 0,
    "schema_cache_max": 50,
    ...
  }
}
```

### 3. Ver Métricas

**Con curl:**
```bash
curl http://localhost:8080/metrics | jq
```

**Respuesta esperada:**
```json
{
  "stats": {
    "total_requests": 10,
    "successful": 9,
    "failed": 1,
    "success_rate": 90.0,
    "avg_response_time_ms": 5234.5
  },
  "recent_requests": [...]
}
```

## Pruebas de Límites

### Probar Límite de Schemas (50)

1. Hacer múltiples requests con diferentes tablas (si tienes acceso)
2. Verificar que el caché no exceda 50:
```bash
curl http://localhost:8080/cache/stats | jq '.cache_stats.schema_cache_size'
```

### Probar Límite de Métricas (1000)

1. Hacer más de 1000 requests
2. Verificar que se limpien automáticamente:
```bash
# Hacer muchos requests
for i in {1..100}; do
  curl -X POST http://localhost:8080/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "Show me contracts"}' > /dev/null 2>&1
done

# Verificar métricas
curl http://localhost:8080/cache/stats | jq '.metrics_stats'
```

### Probar Límite de Conversaciones en Frontend (50)

1. Abrir la aplicación en el navegador
2. Crear más de 50 conversaciones
3. Verificar que solo se mantengan las 50 más recientes

### Probar Límite de Mensajes (100 por conversación)

1. En una conversación, hacer más de 100 preguntas
2. Verificar que solo se muestren los últimos 100 mensajes

## Monitoreo Continuo

### Ver estadísticas en tiempo real:
```bash
watch -n 2 'curl -s http://localhost:8080/cache/stats | jq'
```

### Ver logs de limpieza automática:
```bash
tail -f backend/chatbot.log | grep "🧹"
```

## Verificación de Funcionamiento

✅ **Límites funcionando correctamente si:**
- `schema_cache_size` nunca excede `schema_cache_max` (50)
- `dimensions_not_found_cache_size` nunca excede `dimensions_not_found_cache_max` (100)
- `total_metrics` nunca excede `max_metrics` (1000)
- Los logs muestran mensajes de limpieza cuando se alcanzan los límites

⚠️ **Señales de problemas:**
- Los cachés crecen indefinidamente
- No hay mensajes de limpieza en los logs
- El uso de memoria aumenta constantemente
