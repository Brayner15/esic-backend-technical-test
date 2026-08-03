# Ejemplos de Consumo API

Ejemplos de cómo consumir la API usando cURL, postman o bruno.

## Health Checks

### Verificar disponibilidad de la API

```bash
curl -X GET http://localhost:8000/health
```

**Respuesta esperada (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

### Verificar disponibilidad e conexión con base de datos

```bash
curl -X GET http://localhost:8000/health/ready
```

**Respuesta esperada (200 OK):**
```json
{
  "status": "ready",
  "database": "connected",
  "version": "0.1.0"
}
```

## Crear Solicitudes

### Crear solicitud de acceso a plataforma (prioridad alta)

```bash
curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "EXT-PLAT-001",
    "requester_name": "Juan García",
    "requester_email": "juan.garcia@institution.com",
    "institution_name": "Universidad Central",
    "request_type": "acceso_plataforma",
    "description": "Necesito acceso a la plataforma de gestión académica para consultar mis calificaciones y material de clase",
    "priority": "alta"
  }'
```

### Crear solicitud de soporte técnico (prioridad alta)

```bash
curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "EXT-TECH-001",
    "requester_name": "María López",
    "requester_email": "maria.lopez@institution.com",
    "institution_name": "Instituto Técnico",
    "request_type": "soporte_tecnico",
    "description": "La plataforma no carga correctamente desde mi navegador. Recibo error 500 al intentar acceder",
    "priority": "alta"
  }'
```

### Crear solicitud académica (prioridad media)

```bash
curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "EXT-ACAD-001",
    "requester_name": "Carlos Rodríguez",
    "requester_email": "carlos.r@institution.com",
    "institution_name": "Colegio Profesional",
    "request_type": "academica",
    "description": "Solicito información sobre disponibilidad de cursos de especialización en inteligencia artificial para el próximo semestre",
    "priority": "media"
  }'
```

### Crear solicitud administrativa (prioridad baja)

```bash
curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "EXT-ADMIN-001",
    "requester_name": "Ana Martínez",
    "requester_email": "ana.m@institution.com",
    "institution_name": "Universidad Nacional",
    "request_type": "administrativa",
    "description": "Necesito actualizar mis datos personales en el sistema de registro estudiantes",
    "priority": "baja"
  }'
```

## Consultar Solicitudes

### Obtener una solicitud específica por ID

```bash
curl -X GET http://localhost:8000/solicitudes/1
```

**Respuesta esperada (200 OK):**
```json
{
  "id": 1,
  "request_number": "SOL-A1B2C3D4",
  "external_id": "EXT-PLAT-001",
  "requester_name": "Juan García",
  "requester_email": "juan.garcia@institution.com",
  "institution_name": "Universidad Central",
  "request_type": "acceso_plataforma",
  "description": "Necesito acceso a la plataforma de gestión académica para consultar mis calificaciones y material de clase",
  "priority": "alta",
  "status": "recibida",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Listar todas las solicitudes

```bash
curl -X GET 'http://localhost:8000/solicitudes/?skip=0&limit=100'
```

### Filtrar por estado (recibida, en_proceso, completada, rechazada)

```bash
curl -X GET 'http://localhost:8000/solicitudes/?status=recibida'
```

### Filtrar por tipo de solicitud

```bash
curl -X GET 'http://localhost:8000/solicitudes/?request_type=soporte_tecnico'
```

### Filtrar por prioridad (baja, media, alta)

```bash
curl -X GET 'http://localhost:8000/solicitudes/?priority=alta'
```

### Combinar múltiples filtros

```bash
curl -X GET 'http://localhost:8000/solicitudes/?status=en_proceso&priority=alta&request_type=soporte_tecnico'
```

### Paginar resultados

```bash
# Primera página (primeros 10 resultados)
curl -X GET 'http://localhost:8000/solicitudes/?skip=0&limit=10'

# Segunda página (resultados 10-20)
curl -X GET 'http://localhost:8000/solicitudes/?skip=10&limit=10'
```

## Actualizar Solicitudes

### Cambiar estado de una solicitud

```bash
curl -X PATCH http://localhost:8000/solicitudes/1/estado \
  -H "Content-Type: application/json" \
  -d '{
    "status": "en_proceso"
  }'
```

Estados válidos: `recibida`, `en_proceso`, `completada`, `rechazada`

### Actualizar otros campos (nombre, descripción, prioridad)

```bash
curl -X PUT http://localhost:8000/solicitudes/1 \
  -H "Content-Type: application/json" \
  -d '{
    "priority": "alta",
    "description": "Descripción actualizada con información adicional sobre la solicitud"
  }'
```

Campos actualizables: `requester_name`, `description`, `priority`

## Eliminar Solicitud

```bash
curl -X DELETE http://localhost:8000/solicitudes/1
```

**Respuesta esperada (204 No Content):**
Sin contenido en el body

## Ejemplos de Errores

### Solicitud no encontrada (404)

```bash
curl -X GET http://localhost:8000/solicitudes/9999
```

**Respuesta esperada (404 Not Found):**
```json
{
  "detail": "Solicitud no encontrada"
}
```

### External ID duplicado (409)

Intentar crear una solicitud con un `external_id` que ya existe:

```bash
curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "EXT-PLAT-001",
    "requester_name": "Otro Usuario",
    "requester_email": "otro@institution.com",
    "institution_name": "Otra Institución",
    "request_type": "academica",
    "description": "Intento de crear con external_id duplicado"
  }'
```

**Respuesta esperada (409 Conflict):**
```json
{
  "detail": "Duplicate external_id: EXT-PLAT-001"
}
```

### Email inválido (422)

```bash
curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "EXT-ERR-001",
    "requester_name": "Juan Pérez",
    "requester_email": "email-invalido",
    "institution_name": "Institución",
    "request_type": "academica",
    "description": "Este email no es válido"
  }'
```

**Respuesta esperada (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "requester_email"],
      "msg": "invalid email format",
      "input": "email-invalido"
    }
  ]
}
```

### Descripción muy corta (422)

```bash
curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "EXT-ERR-002",
    "requester_name": "Juan Pérez",
    "requester_email": "juan@example.com",
    "institution_name": "Institución",
    "request_type": "academica",
    "description": "Corta"
  }'
```

**Respuesta esperada (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "description"],
      "msg": "String should have at least 10 characters",
      "input": "Corta",
      "ctx": {"min_length": 10}
    }
  ]
}
```

### Tipo de solicitud inválido (422)

```bash
curl -X POST http://localhost:8000/solicitudes/ \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "EXT-ERR-003",
    "requester_name": "Juan Pérez",
    "requester_email": "juan@example.com",
    "institution_name": "Institución",
    "request_type": "tipo_invalido",
    "description": "Tipo de solicitud no válido"
  }'
```

**Respuesta esperada (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["body", "request_type"],
      "msg": "Input should be 'acceso_plataforma', 'soporte_tecnico', 'academica' or 'administrativa'",
      "input": "tipo_invalido"
    }
  ]
}
```

## Documentación Interactiva

Acceder a la documentación automática de la API:

### Swagger UI
```
http://localhost:8000/docs
```

## Ejecutar Consumer Service

El servicio consumidor se ejecuta automáticamente al hacer `docker compose up`, pero si deseas ejecutarlo manualmente:

```bash
# Desde la raíz del proyecto
python -m consumer.consumer
```

O con Docker:

```bash
docker run --rm -it --network esic_network \
  --build-arg context=. \
  --build-arg dockerfile=Dockerfile.consumer \
  esic_consumer
```
