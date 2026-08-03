# Ejemplos de Logs Estructurados en JSON

La aplicación genera logs estructurados en formato JSON que permiten un análisis completo de todas las operaciones. Los logs incluyen:

- **Timestamp**: Hora exacta en formato ISO-8601
- **Level**: Nivel del log (INFO, WARNING, ERROR)
- **Logger**: Nombre del módulo que genera el log
- **Correlation ID**: ID único para rastrear una solicitud a través del sistema
- **Message**: Tipo de evento (p.ej., "create_request_success")
- **Campos contextuales**: Información específica del evento

## Ubicación de Logs

```
logs/
├── application.log     # Logs del backend
└── consumer.log        # Logs del servicio consumidor
```

## Ejemplos de Logs del Backend

### 1. Inicio de Aplicación

```json
{
  "timestamp": "2024-01-15T10:00:00.000000",
  "level": "INFO",
  "logger": "app.main",
  "message": "application_startup",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "environment": "development"
}
```

### 2. Request Iniciado (Middleware)

```json
{
  "timestamp": "2024-01-15T10:00:05.123456",
  "level": "INFO",
  "logger": "app.middleware",
  "message": "request_started",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "request_method": "POST",
  "request_path": "/solicitudes/"
}
```

### 3. Intento de Crear Solicitud

```json
{
  "timestamp": "2024-01-15T10:00:05.234567",
  "level": "INFO",
  "logger": "app.api.routes",
  "message": "create_request_attempt",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "external_id": "EXT-001",
  "request_type": "soporte_tecnico",
  "priority": "alta"
}
```

### 4. Solicitud Creada Exitosamente

```json
{
  "timestamp": "2024-01-15T10:00:05.345678",
  "level": "INFO",
  "logger": "app.api.routes",
  "message": "create_request_success",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "external_id": "EXT-001",
  "request_id": 1,
  "request_number": "SOL-A1B2C3D4"
}
```

### 5. Request Completado (Middleware)

```json
{
  "timestamp": "2024-01-15T10:00:05.456789",
  "level": "INFO",
  "logger": "app.middleware",
  "message": "request_completed",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "request_method": "POST",
  "request_path": "/solicitudes/",
  "status_code": 201,
  "duration_ms": 333.22
}
```

### 6. Intento de Obtener Solicitud

```json
{
  "timestamp": "2024-01-15T10:00:10.567890",
  "level": "INFO",
  "logger": "app.api.routes",
  "message": "get_request_attempt",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "request_id": 1
}
```

### 7. Solicitud Obtenida Exitosamente

```json
{
  "timestamp": "2024-01-15T10:00:10.678901",
  "level": "INFO",
  "logger": "app.api.routes",
  "message": "get_request_success",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "request_id": 1,
  "status": "recibida"
}
```

### 8. Solicitud No Encontrada

```json
{
  "timestamp": "2024-01-15T10:00:15.789012",
  "level": "WARNING",
  "logger": "app.api.routes",
  "message": "get_request_not_found",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "request_id": 9999
}
```

### 9. External ID Duplicado

```json
{
  "timestamp": "2024-01-15T10:00:20.890123",
  "level": "WARNING",
  "logger": "app.api.routes",
  "message": "create_request_duplicate",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "external_id": "EXT-001",
  "error_detail": "Duplicate external_id: EXT-001"
}
```

### 10. Actualizar Estado Exitosamente

```json
{
  "timestamp": "2024-01-15T10:00:25.901234",
  "level": "INFO",
  "logger": "app.api.routes",
  "message": "update_status_success",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "request_id": 1,
  "new_status": "en_proceso"
}
```

### 11. Listar Solicitudes con Filtros

```json
{
  "timestamp": "2024-01-15T10:00:30.012345",
  "level": "INFO",
  "logger": "app.api.routes",
  "message": "list_requests",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "skip": 0,
  "limit": 100,
  "filters": {
    "status": "recibida",
    "request_type": "soporte_tecnico",
    "priority": "alta"
  }
}
```

### 12. Error de Conexión a Base de Datos

```json
{
  "timestamp": "2024-01-15T10:00:35.123456",
  "level": "ERROR",
  "logger": "app.main",
  "message": "database_connection_failed",
  "correlation_id": "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2",
  "error_detail": "connection to server at \"postgres\" (172.18.0.2), port 5432 failed"
}
```

## Ejemplos de Logs del Consumer

### 1. Inicio del Consumidor

```json
{
  "timestamp": "2024-01-15T10:05:00.000000",
  "level": "INFO",
  "logger": "consumer",
  "message": "consumer_started",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "backend_url": "http://backend:8000"
}
```

### 2. Health Check Exitoso

```json
{
  "timestamp": "2024-01-15T10:05:05.000000",
  "level": "INFO",
  "logger": "consumer",
  "message": "health_check_success",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "service": "backend",
  "status_code": 200
}
```

### 3. Readiness Check Exitoso

```json
{
  "timestamp": "2024-01-15T10:05:10.000000",
  "level": "INFO",
  "logger": "consumer",
  "message": "readiness_check_success",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "service": "backend",
  "database": "connected",
  "status_code": 200
}
```

### 4. Crear Solicitud - Intento

```json
{
  "timestamp": "2024-01-15T10:05:15.000000",
  "level": "INFO",
  "logger": "consumer",
  "message": "create_request_success",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "external_id": "EXT-001",
  "request_id": 1,
  "request_number": "SOL-A1B2C3D4",
  "attempt": 1,
  "status_code": 201
}
```

### 5. Conflicto - Solicitud Duplicada

```json
{
  "timestamp": "2024-01-15T10:05:20.000000",
  "level": "WARNING",
  "logger": "consumer",
  "message": "create_request_conflict",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "external_id": "EXT-001",
  "status_code": 409,
  "error_detail": "Duplicate external_id"
}
```

### 6. Error Retryable - Timeout

```json
{
  "timestamp": "2024-01-15T10:05:25.000000",
  "level": "WARNING",
  "logger": "consumer",
  "message": "create_request_timeout",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "external_id": "EXT-002",
  "retry_attempt": 1,
  "max_retries": 3
}
```

### 7. Error Retryable - Error de Conexión

```json
{
  "timestamp": "2024-01-15T10:05:30.000000",
  "level": "WARNING",
  "logger": "consumer",
  "message": "create_request_connection_error",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "external_id": "EXT-003",
  "retry_attempt": 1,
  "max_retries": 3
}
```

### 8. Error Retryable - 500 Server Error

```json
{
  "timestamp": "2024-01-15T10:05:35.000000",
  "level": "WARNING",
  "logger": "consumer",
  "message": "create_request_retryable_error",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "external_id": "EXT-004",
  "status_code": 500,
  "retry_attempt": 1,
  "max_retries": 3
}
```

### 9. Error Permanente - 422 Validation Error

```json
{
  "timestamp": "2024-01-15T10:05:40.000000",
  "level": "ERROR",
  "logger": "consumer",
  "message": "create_request_client_error",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "external_id": "EXT-005",
  "status_code": 422,
  "attempt": 1,
  "retry": false
}
```

### 10. Max Retries Exceeded

```json
{
  "timestamp": "2024-01-15T10:05:50.000000",
  "level": "ERROR",
  "logger": "consumer",
  "message": "create_request_max_retries_exceeded",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "external_id": "EXT-006",
  "max_retries": 3
}
```

### 11. Obtener Solicitud - Exitoso

```json
{
  "timestamp": "2024-01-15T10:05:55.000000",
  "level": "INFO",
  "logger": "consumer",
  "message": "get_request_success",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "external_id": "EXT-001",
  "request_id": 1,
  "status": "recibida",
  "status_code": 200
}
```

### 12. Resumen de Ejecución

```json
{
  "timestamp": "2024-01-15T10:06:00.000000",
  "level": "INFO",
  "logger": "consumer",
  "message": "execution_summary",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "total_attempts": 5,
  "successful": 4,
  "failed": 0,
  "conflicts": 1
}
```

## Herramientas para Analizar Logs

### 1. Filtrar logs por Correlation ID

```bash
# Backend
cat logs/application.log | grep "x7y8z9w0-1a2b-3c4d-5e6f-g7h8i9j0k1l2"

# Consumer
cat logs/consumer.log | grep "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6"
```

### 2. Filtrar por nivel de log

```bash
# Solo errores
grep '"level":"ERROR"' logs/application.log

# Solo warnings
grep '"level":"WARNING"' logs/application.log

# Solo info
grep '"level":"INFO"' logs/application.log
```

### 3. Filtrar por tipo de evento

```bash
# Solicitudes creadas
grep "create_request_success" logs/application.log

# Errores de conexión a BD
grep "database_connection_failed" logs/application.log

# Reintentos del consumer
grep "retry" logs/consumer.log
```

### 4. Medir tiempos de respuesta

```bash
# Extraer duraciones (requiere jq)
cat logs/application.log | grep "request_completed" | \
  jq '.duration_ms' | \
  awk '{sum+=$1; count++} END {print "Promedio:", sum/count, "ms"}'
```

### 5. Contar solicitudes por estado

```bash
grep "get_request_success" logs/application.log | \
  jq '.status' | sort | uniq -c
```

## Ventajas del Logging Estructurado en JSON

✅ **Trazabilidad**: Cada request tiene un Correlation ID único  
✅ **Análisis**: Fácil parsear y filtrar logs  
✅ **Monitoreo**: Integración con herramientas de logging centralizadas (ELK, Datadog, CloudWatch)  
✅ **Rendimiento**: Medición automática de tiempos de respuesta  
✅ **Debugging**: Contexto completo en cada log  
✅ **Auditoría**: Registro detallado de todas las operaciones  

## Siguiente Paso: Centralización de Logs

Para producción, se recomienda:

1. **ELK Stack** (Elasticsearch, Logstash, Kibana) - On-premise
2. **AWS CloudWatch** - Cloud
3. **Datadog** - SaaS
4. **Splunk** - Enterprise

Todos estos servicios pueden consumir logs en formato JSON directamente.
