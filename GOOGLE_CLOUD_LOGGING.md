# 📝 Google Cloud Logging - Configuración

## 🎯 ¿Qué es Google Cloud Logging?

Google Cloud Logging es un servicio de GCP que permite centralizar y gestionar logs de aplicaciones. Los logs se almacenan en Cloud Logging y pueden ser consultados, analizados y monitoreados desde la consola de GCP.

## 📋 Información para RSE (Habilitar el Servicio)

### Nombre del Servicio
**Cloud Logging API**

### Nombre de la API (para habilitar)
```
logging.googleapis.com
```

### Comando para Habilitar
```bash
gcloud services enable logging.googleapis.com --project=<PROJECT_ID>
```

**Ejemplo con el proyecto actual:**
```bash
gcloud services enable logging.googleapis.com --project=bunge-de-poc-insumos
```

### Permisos Necesarios

**Para escribir logs** (requerido):
- `roles/logging.logWriter` - Permite escribir logs a Cloud Logging
- O el permiso específico: `logging.logEntries.create`

**Para leer/buscar logs** (opcional, solo para verificación):
- `roles/logging.viewer` - Permite leer logs públicos
- O `roles/logging.privateLogViewer` - Permite leer logs privados

**Nota**: Si solo quieres enviar logs, solo necesitas `roles/logging.logWriter`. El permiso de lectura es solo útil para verificar que los logs se están enviando correctamente.

### Verificar si está Habilitado
```bash
gcloud services list --enabled --project=<PROJECT_ID> | grep logging
```

O desde la consola de GCP:
1. Ir a **APIs & Services** > **Enabled APIs**
2. Buscar "Cloud Logging API"
3. Verificar que esté habilitada

---

## 🔧 Configuración en la Aplicación

### 1. Instalar la Dependencia

Ya está agregada en `requirements.txt`:
```
google-cloud-logging==3.11.0
```

Instalar con:
```bash
pip install google-cloud-logging
```

### 2. Variables de Entorno

Asegúrate de tener configurado:
```env
PROJECT_ID=bunge-de-poc-insumos
```

### 3. Cómo Funciona

El código en `backend/app/logger.py` ahora:

1. **Intenta inicializar Google Cloud Logging** al arrancar
2. **Si está disponible**: Los logs se envían automáticamente a GCP
3. **Si NO está disponible**: Continúa con logging local (archivo + consola)

**No requiere cambios adicionales** - funciona automáticamente si la API está habilitada.

---

## ✅ Verificar que Funciona

### Opción 1: Verificar si la API está Habilitada
```bash
cd backend
python check_logging_api.py
```
Este script solo verifica si la API está habilitada y si el cliente se puede inicializar.

### Opción 2: Ver Logs en la Aplicación
Al iniciar la aplicación, deberías ver en los logs:
```
✅ Google Cloud Logging enabled - Logs will be sent to GCP
```

Si no está habilitado, verás:
```
⚠️  Google Cloud Logging not available: [error]
   Continuing with local logging only
```

### Opción 3: Verificar en Cloud Console (Manual)
1. Ir a **Cloud Console** > **Logging** > **Logs Explorer**
2. Filtrar por:
   - Resource: `global`
   - Log name: `nl2sql_chatbot` o el nombre que uses
3. Deberías ver los logs de la aplicación

---

## 📊 Ventajas de Usar Cloud Logging

1. **Centralización**: Todos los logs en un solo lugar
2. **Búsqueda Avanzada**: Filtros y queries complejas
3. **Retención**: Logs almacenados según políticas de retención
4. **Integración**: Se integra con otros servicios de GCP (Monitoring, Alerting)
5. **Escalabilidad**: Maneja grandes volúmenes de logs automáticamente
6. **Análisis**: Puedes crear dashboards y alertas basadas en logs

---

## 🔍 Estructura de los Logs

Los logs se envían con la siguiente estructura:

- **Logger Name**: `nl2sql_chatbot`
- **Level**: INFO, WARNING, ERROR
- **Message**: El mensaje formateado
- **Metadata**: Timestamp, request_id, etc. (automático)

### Ejemplo de Log en Cloud Logging

```json
{
  "timestamp": "2025-01-13T10:30:00Z",
  "severity": "INFO",
  "logName": "projects/bunge-de-poc-insumos/logs/nl2sql_chatbot",
  "textPayload": "ℹ️  Nuevo request [abc123]: ¿Cuántos contratos hay?",
  "labels": {
    "python_logger": "nl2sql_chatbot"
  }
}
```

---

## 🚨 Troubleshooting

### Error: "API not enabled"
**Síntoma**: Error al inicializar el cliente o mensaje "API not enabled"  
**Solución**: RSE debe habilitar `logging.googleapis.com`
```bash
gcloud services enable logging.googleapis.com --project=<PROJECT_ID>
```

### Error: "Permission 'logging.logEntries.create' denied" (403)
**Síntoma**: Al enviar logs aparece "Permission denied" (403)  
**Causa**: Falta el permiso para escribir logs  
**Solución**: RSE debe otorgar el rol `roles/logging.logWriter`

**Para usuario:**
```bash
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member='user:tu-email@dominio.com' \
  --role='roles/logging.logWriter'
```

**Para service account:**
```bash
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member='serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com' \
  --role='roles/logging.logWriter'
```

### Error: "Module not found"
**Síntoma**: `ImportError: No module named 'google.cloud.logging'`  
**Solución**: Instalar dependencia:
```bash
pip install google-cloud-logging
```

### Los logs no aparecen en Cloud Console
1. **Verificar que la API esté habilitada**: `python check_logging_api.py`
2. **Verificar permisos**: La cuenta debe tener `roles/logging.logWriter`
3. **Esperar unos segundos**: Los logs pueden tardar 1–2 minutos en aparecer
4. **Verificar el filtro en Logs Explorer**: Usar `logName="projects/PROJECT_ID/logs/nl2sql_chatbot"`
5. **Verificar que estás en el proyecto correcto** en la consola de GCP

---

## 📝 Notas Importantes

- **Logging Local Sigue Funcionando**: Incluso con Cloud Logging habilitado, los logs locales (archivo `chatbot.log`) siguen funcionando
- **Sin Cambios en el Código**: El código actual funciona con o sin Cloud Logging
- **Fallback Automático**: Si Cloud Logging falla, la aplicación continúa con logging local
- **Rendimiento**: Cloud Logging es asíncrono y no afecta el rendimiento de la aplicación

---

## 🔗 Referencias

- [Documentación de Cloud Logging](https://cloud.google.com/logging/docs)
- [Python Client Library](https://cloud.google.com/logging/docs/reference/libraries#client-libraries-usage-python)
- [Habilitar APIs en GCP](https://cloud.google.com/apis/docs/getting-started)

---

## 📧 Contacto RSE

Si necesitas habilitar el servicio, proporciona esta información:

**Servicio**: Cloud Logging API  
**API Name**: `logging.googleapis.com`  
**Proyecto**: `bunge-de-poc-insumos`  
**Comando**: `gcloud services enable logging.googleapis.com --project=bunge-de-poc-insumos`  
**Permisos necesarios**: `roles/logging.logWriter` para la cuenta de servicio
