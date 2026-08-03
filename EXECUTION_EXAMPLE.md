# Ejemplo de Ejecución del Sistema

## Simulación de Ejecución Completa

Este documento muestra un ejemplo completo de ejecución del sistema con logs, requests y respuestas.

## 1. Startup de los Servicios

```bash
$ docker compose up --build
```

### Logs de Startup

```json
2024-01-15T10:00:00.000000+00:00 INFO app.main - {
  "timestamp": "2024-01-15T10:00:00.000000",
  "level": "INFO",
  "logger": "app.main",
  "message": "application_startup",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "environment": "development"
}
```

## 2. Verificar Health Check

```bash
$ curl http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

**Logs generados:**
```json
{
  "timestamp": "2024-01-15T10:00:05.123456",
  "level": "INFO",
  "logger": "app.middleware",
  "message": "request_started",
  "correlation_id": "x1y2z3a4-b5c6-d7e8-f9g0-h1i2j3k4l5m6",
  "request_method": "GET",
  "request_path": "/health"
}
```

```json
{
  "timestamp": "2024-01-15T10:00:05.234567",
  "level": "INFO",
  "logger": "app.middleware",
  "message": "request_completed",
  "correlation_id": "x1y2z3a4-b5c6-d7e8-f9g0-h1i2j3k4l5m6",
  "request_method": "GET",
  "request_path": "/health",
  "status_code": 200,
  "duration_ms": 111.11
}
```

## 3. Verificar Readiness Check

```bash
$ curl http://localhost:8000/health/ready
```

**Respuesta:**
```json
{
  "status": "ready",
  "database": "connected",
  "version": "0.1.0"
}
```

## 4. Crear Solicitudes Válidas

### Request 1: Solicitud de Soporte Técnico (Alta Prioridad)

```bash
$ curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: req-tech-001" \
  -d '{
    "external_id": "EXT-TECH-001",
    "requester_name": "Juan Pérez",
    "requester_email": "juan@university.edu",
    "institution_name": "Universidad Central",
    "request_type": "soporte_tecnico",
    "description": "La plataforma de aprendizaje virtual no carga correctamente desde mi navegador. Recibo error 500 al intentar acceder a los materiales del curso",
    "priority": "alta"
  }'
```

**Respuesta (201 Created):**
```json
{
  "id": 1,
  "request_number": "SOL-A1B2C3D4",
  "external_id": "EXT-TECH-001",
  "requester_name": "Juan Pérez",
  "requester_email": "juan@university.edu",
  "institution_name": "Universidad Central",
  "request_type": "soporte_tecnico",
  "description": "La plataforma de aprendizaje virtual no carga correctamente desde mi navegador. Recibo error 500 al intentar acceder a los materiales del curso",
  "priority": "alta",
  "status": "recibida",
  "created_at": "2024-01-15T10:00:10.000000",
  "updated_at": "2024-01-15T10:00:10.000000"
}
```

**Logs generados:**
```json
{
  "timestamp": "2024-01-15T10:00:10.111111",
  "level": "INFO",
  "logger": "app.api.routes",
  "message": "create_request_attempt",
  "correlation_id": "req-tech-001",
  "external_id": "EXT-TECH-001",
  "request_type": "soporte_tecnico",
  "priority": "alta"
}
```

```json
{
  "timestamp": "2024-01-15T10:00:10.222222",
  "level": "INFO",
  "logger": "app.services",
  "message": "service_create_request_success",
  "correlation_id": "req-tech-001",
  "external_id": "EXT-TECH-001",
  "request_id": 1,
  "request_number": "SOL-A1B2C3D4"
}
```

### Request 2: Solicitud Académica (Prioridad Media)

```bash
$ curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: req-acad-001" \
  -d '{
    "external_id": "EXT-ACAD-001",
    "requester_name": "María García",
    "requester_email": "maria@university.edu",
    "institution_name": "Instituto Técnico",
    "request_type": "academica",
    "description": "Solicito información sobre la disponibilidad de cursos de especialización en inteligencia artificial para el próximo semestre",
    "priority": "media"
  }'
```

**Respuesta (201 Created):**
```json
{
  "id": 2,
  "request_number": "SOL-E5F6G7H8",
  "external_id": "EXT-ACAD-001",
  "requester_name": "María García",
  "requester_email": "maria@university.edu",
  "institution_name": "Instituto Técnico",
  "request_type": "academica",
  "description": "Solicito información sobre la disponibilidad de cursos de especialización en inteligencia artificial para el próximo semestre",
  "priority": "media",
  "status": "recibida",
  "created_at": "2024-01-15T10:00:15.000000",
  "updated_at": "2024-01-15T10:00:15.000000"
}
```

## 5. Intentar Crear Duplicado (Error Esperado)

```bash
$ curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: req-dup-001" \
  -d '{
    "external_id": "EXT-TECH-001",
    "requester_name": "Otro Usuario",
    "requester_email": "otro@university.edu",
    "institution_name": "Otra Institución",
    "request_type": "administrativa",
    "description": "Intento de crear con external_id duplicado",
    "priority": "baja"
  }'
```

**Respuesta (409 Conflict):**
```json
{
  "detail": "Solicitud con external_id 'EXT-TECH-001' ya existe (ID: 1)"
}
```

**Logs generados:**
```json
{
  "timestamp": "2024-01-15T10:00:20.111111",
  "level": "WARNING",
  "logger": "app.services",
  "message": "service_create_request_duplicate_detected",
  "correlation_id": "req-dup-001",
  "external_id": "EXT-TECH-001",
  "existing_request_id": 1
}
```

## 6. Listar Solicitudes con Filtros

### Listar todas las solicitudes

```bash
$ curl 'http://localhost:8000/solicitudes/?skip=0&limit=100'
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 2,
    "request_number": "SOL-E5F6G7H8",
    "external_id": "EXT-ACAD-001",
    "requester_name": "María García",
    "requester_email": "maria@university.edu",
    "institution_name": "Instituto Técnico",
    "request_type": "academica",
    "description": "Solicito información sobre la disponibilidad de cursos de especialización en inteligencia artificial para el próximo semestre",
    "priority": "media",
    "status": "recibida",
    "created_at": "2024-01-15T10:00:15.000000",
    "updated_at": "2024-01-15T10:00:15.000000"
  },
  {
    "id": 1,
    "request_number": "SOL-A1B2C3D4",
    "external_id": "EXT-TECH-001",
    "requester_name": "Juan Pérez",
    "requester_email": "juan@university.edu",
    "institution_name": "Universidad Central",
    "request_type": "soporte_tecnico",
    "description": "La plataforma de aprendizaje virtual no carga correctamente desde mi navegador. Recibo error 500 al intentar acceder a los materiales del curso",
    "priority": "alta",
    "status": "recibida",
    "created_at": "2024-01-15T10:00:10.000000",
    "updated_at": "2024-01-15T10:00:10.000000"
  }
]
```

### Filtrar por prioridad alta

```bash
$ curl 'http://localhost:8000/solicitudes/?priority=alta'
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "request_number": "SOL-A1B2C3D4",
    "external_id": "EXT-TECH-001",
    "requester_name": "Juan Pérez",
    "priority": "alta",
    "status": "recibida",
    ...
  }
]
```

## 7. Obtener Solicitud Específica

```bash
$ curl 'http://localhost:8000/solicitudes/1'
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "request_number": "SOL-A1B2C3D4",
  "external_id": "EXT-TECH-001",
  "requester_name": "Juan Pérez",
  "requester_email": "juan@university.edu",
  "institution_name": "Universidad Central",
  "request_type": "soporte_tecnico",
  "description": "La plataforma de aprendizaje virtual no carga correctamente desde mi navegador. Recibo error 500 al intentar acceder a los materiales del curso",
  "priority": "alta",
  "status": "recibida",
  "created_at": "2024-01-15T10:00:10.000000",
  "updated_at": "2024-01-15T10:00:10.000000"
}
```

## 8. Actualizar Estado de Solicitud

```bash
$ curl -X PATCH 'http://localhost:8000/solicitudes/1/estado' \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: req-status-001" \
  -d '{
    "status": "en_proceso"
  }'
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "request_number": "SOL-A1B2C3D4",
  "external_id": "EXT-TECH-001",
  "requester_name": "Juan Pérez",
  "status": "en_proceso",
  ...
}
```

**Logs generados:**
```json
{
  "timestamp": "2024-01-15T10:00:25.111111",
  "level": "INFO",
  "logger": "app.services",
  "message": "service_update_status_success",
  "correlation_id": "req-status-001",
  "request_id": 1,
  "old_status": "recibida",
  "new_status": "en_proceso"
}
```

## 9. Error: Solicitud No Encontrada

```bash
$ curl 'http://localhost:8000/solicitudes/99999'
```

**Respuesta (404 Not Found):**
```json
{
  "detail": "Solicitud con ID 99999 no encontrada"
}
```

**Logs generados:**
```json
{
  "timestamp": "2024-01-15T10:00:30.111111",
  "level": "WARNING",
  "logger": "app.api.routes",
  "message": "get_request_not_found",
  "correlation_id": "some-uuid",
  "request_id": 99999
}
```

## 10. Ejecutar Consumer Service

```bash
$ docker compose run consumer
```

### Logs del Consumer

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

```json
{
  "timestamp": "2024-01-15T10:05:10.000000",
  "level": "INFO",
  "logger": "consumer",
  "message": "create_request_success",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "external_id": "EXT-001",
  "request_id": 3,
  "request_number": "SOL-I9J0K1L2",
  "attempt": 1,
  "status_code": 201
}
```

```json
{
  "timestamp": "2024-01-15T10:05:45.000000",
  "level": "INFO",
  "logger": "consumer",
  "message": "execution_summary",
  "correlation_id": "c1d2e3f4-5678-90ab-cdef-g1h2i3j4k5l6",
  "total_attempts": 5,
  "successful": 5,
  "failed": 0,
  "conflicts": 0
}
```

## Resumen de Ejecución

| Métrica | Valor |
|---------|-------|
| Solicitudes Creadas | 5 |
| Solicitudes Exitosas | 5 |
| Conflictos (Duplicados) | 0 |
| Errores Permanentes | 0 |
| Tiempo Total | ~45 segundos |
| Logs Generados | 25+ eventos |

## Archivos de Logs Generados

```
logs/
├── application.log     (150+ líneas de JSON)
└── consumer.log        (80+ líneas de JSON)
```

Cada línea es un evento JSON independiente que puede ser indexado, buscado y analizado con herramientas como jq, grep, o ELK Stack.
