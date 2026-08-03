# ESIC Backend Technical Test

Un servicio backend moderno, escalable y robusto para gestionar solicitudes institucionales. Desarrollado con Python, FastAPI y PostgreSQL, con énfasis en código limpio, buenas prácticas, validaciones avanzadas y observabilidad.

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Tests](https://img.shields.io/badge/tests-21%2F21%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📋 Descripción General

Este proyecto implementa un servicio backend profesional que permite:
- ✅ Crear, leer, actualizar y eliminar solicitudes institucionales
- ✅ Gestionar el ciclo de vida de solicitudes (recibida, en proceso, completada, rechazada)
- ✅ Integración con sistemas externos simulados
- ✅ API RESTful con documentación automática (Swagger)
- ✅ Base de datos relacional con PostgreSQL
- ✅ Logging estructurado en JSON con trazabilidad
- ✅ Manejo robusto de concurrencia y duplicados
- ✅ Containerización con Docker y orquestación con Docker Compose
- ✅ Suite completa de pruebas automatizadas (21 tests)

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    API Routes                         │   │
│  │  (GET, POST, PUT, PATCH, DELETE /solicitudes)        │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Business Logic (Services)                │   │
│  │  InstitutionalRequestService                          │   │
│  │  - Validaciones avanzadas                             │   │
│  │  - Manejo de duplicados                               │   │
│  │  - Transacciones atómicas                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Data Access (SQLAlchemy ORM)              │   │
│  │            Logging (JSON, Correlation IDs)           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
         ┌──────────────────────────────────────┐
         │    PostgreSQL Database               │
         │  (institutional_requests table)      │
         │  (Índices optimizados)               │
         └──────────────────────────────────────┘

         ┌──────────────────────────────────────┐
         │   Consumer Service (Simulated)       │
         │  (Retry logic, Health checks)        │
         └──────────────────────────────────────┘
```

## 🛠️ Tecnologías

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Lenguaje | Python | 3.10+ |
| Framework Web | FastAPI | 0.104.1 |
| Servidor ASGI | Uvicorn | 0.24.0 |
| ORM | SQLAlchemy | 2.0.23 |
| Validación | Pydantic | 2.5.0 |
| Base de Datos | PostgreSQL | 15 |
| HTTP Client | httpx | 0.25.2 |
| Logging JSON | python-json-logger | 2.0.7 |
| Testing | pytest | 7.4.3 |
| Containerización | Docker | Latest |

## 📦 Estructura del Proyecto

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                   # Punto de entrada FastAPI
│   ├── config.py                 # Configuración y variables de entorno
│   ├── database.py               # Configuración SQLAlchemy
│   ├── models.py                 # Modelos de BD (SQLAlchemy)
│   ├── schemas.py                # Esquemas Pydantic (DTOs)
│   ├── services.py               # Lógica de negocio con validaciones
│   ├── logging_config.py         # Configuración de logging JSON
│   ├── middleware.py             # Middleware HTTP para logging
│   └── api/
│       ├── __init__.py
│       └── routes.py             # Endpoints de la API
├── consumer/
│   ├── __init__.py
│   ├── consumer.py               # Servicio consumidor con reintentos
│   └── requirements.txt
├── external_service/
│   ├── __init__.py
│   └── main.py                   # Servicio externo simulado
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Configuración pytest
│   ├── test_api.py              # Tests de endpoints (13 tests)
│   └── test_concurrency.py      # Tests de concurrencia (8 tests)
├── logs/
│   ├── application.log           # Logs del backend
│   └── consumer.log              # Logs del consumidor
├── .env.example                  # Variables de entorno template
├── .gitignore
├── compose.yaml            # Orquestación de servicios
├── Dockerfile                    # Imagen backend
├── Dockerfile.consumer           # Imagen consumer
├── Dockerfile.external           # Imagen servicio externo
├── init_db.sql                   # Script inicialización BD
├── requirements.txt              # Dependencias
├── pyproject.toml               # Configuración del proyecto
├── README.md                     # Este archivo
├── EXAMPLES.md                   # Ejemplos de consumo API (curl)
├── TESTING.md                    # Guía de pruebas
├── EXECUTION_EXAMPLE.md          # Ejemplo de ejecución completa
└── LOGS_EXAMPLE.md              # Ejemplos de logs JSON
```

## 🚀 Inicio Rápido

### Requisitos Previos
- Docker y Docker Compose instalados
- Git

### Instalación y Ejecución

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/Brayner15/esic-backend-technical-test.git
   cd esic-backend-technical-test
   ```

2. **Crear archivo .env (requerido)**
   
   Copia el archivo `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
   
   El archivo `.env` contiene todas las credenciales de la base de datos:
   ```env
   # Database Configuration (PostgreSQL)
   DATABASE_USER=esic_user
   DATABASE_PASSWORD=esic_password
   DATABASE_NAME=esic_db
   DATABASE_PORT=5432
   DATABASE_URL=postgresql://esic_user:esic_password@postgres:5432/esic_db
   
   # Puedes cambiar estos valores según necesites
   # Importante: nunca subas .env a Git
   ```
   
   **Nota:** El archivo `.env` está en `.gitignore` por seguridad. Cada entorno (dev, staging, prod) tendrá sus propias credenciales.

3. **Levantar los servicios**
   ```bash
   docker compose up --build
   ```

   Esto inicia:
   - **PostgreSQL** en puerto 5432
   - **Backend API** en puerto 8000
   - **Servicio Externo** en puerto 8001
   - **Consumer** (ejecuta una sola vez)

4. **Verificar que todo funciona**
   ```bash
   curl http://localhost:8000/health
   ```

   Respuesta esperada:
   ```json
   {
     "status": "healthy",
     "version": "0.1.0",
     "environment": "development"
   }
   ```

### Detener los servicios
```bash
docker compose down

# Eliminar datos persistentes
docker compose down -v
```

## 📚 Documentación

| Documento | Descripción |
|-----------|-----------|
| [EXAMPLES.md](EXAMPLES.md) | Ejemplos de consumo de API con curl |
| [TESTING.md](TESTING.md) | Guía completa de pruebas y cobertura |
| [EXECUTION_EXAMPLE.md](EXECUTION_EXAMPLE.md) | Ejemplo de ejecución con logs |
| [LOGS_EXAMPLE.md](LOGS_EXAMPLE.md) | Ejemplos de logs en JSON |

## 📡 API Endpoints

### Health & Readiness
- `GET /health` - Verificar disponibilidad
- `GET /health/ready` - Verificar BD + disponibilidad

### CRUD de Solicitudes
- `POST /solicitudes/` - Crear solicitud (201)
- `GET /solicitudes/` - Listar con filtros
- `GET /solicitudes/{id}` - Obtener por ID
- `PUT /solicitudes/{id}` - Actualizar campos
- `PATCH /solicitudes/{id}/estado` - Cambiar estado
- `DELETE /solicitudes/{id}` - Eliminar

**Filtros en GET /solicitudes/:**
- `status`: recibida, en_proceso, completada, rechazada
- `request_type`: acceso_plataforma, soporte_tecnico, academica, administrativa
- `priority`: baja, media, alta

## 🧪 Tests

**21 tests automatizados** cubriendo:
- ✅ 13 tests de API (endpoints, validaciones, errores)
- ✅ 8 tests de concurrencia (duplicados, race conditions)
- ✅ **94% code coverage**
- ✅ Timeout y reintentos del consumer

```bash
# Ejecutar tests localmente
pip install -r requirements.txt pytest pytest-asyncio
pytest tests/ -v --cov=app

# Ejecutar en Docker
docker compose run --rm backend pytest tests/ -v
```

## 📊 Validaciones & Seguridad

✅ Validación de email con Pydantic  
✅ Restricción única en external_id  
✅ Manejo robusto de duplicados (409)  
✅ Transacciones ACID en BD  
✅ Protección contra SQL injection (SQLAlchemy ORM)  
✅ Códigos HTTP coherentes  
✅ Mensajes de error no técnicos  
✅ Correlation IDs para trazabilidad  
✅ Type hints completos  

## 📈 Logging Estructurado

Logs en formato **JSON** con:
- Timestamps ISO-8601
- Correlation IDs (X-Correlation-ID header)
- Niveles: INFO, WARNING, ERROR
- Duración de requests (ms)
- IDs de solicitud
- Detalles de errores

Archivos:
- `logs/application.log` - Backend
- `logs/consumer.log` - Consumer

## 🔧 Variables de Entorno

Ver `.env.example` para la lista completa. Principales:

```env
# Aplicación
APP_ENV=development
APP_DEBUG=True
APP_LOG_LEVEL=INFO

# Base de datos
DATABASE_URL=postgresql://user:pass@postgres:5432/dbname
DATABASE_POOL_SIZE=20

# Servicio externo
EXTERNAL_SERVICE_URL=http://external-service:8001

# Seguridad
SECRET_KEY=change-in-production
```

## 🏛️ Decisiones Técnicas

### FastAPI
Elegido por documentación automática, validación nativa, tipo hints y rendimiento.

### SQLAlchemy 2.0
ORM moderno con soporte async, seguridad contra SQL injection y migrations.

### PostgreSQL
RDBMS confiable con índices eficientes, transacciones ACID, soporte para enums.

### Logging JSON
Estructura consistente para integración con ELK Stack, CloudWatch o Datadog.

### Docker Compose
Reproducibilidad de ambiente de desarrollo, parity con producción.

### Concurrencia
Validación previa + IntegrityError handling = garantía de no-duplicados.

## ⚠️ Limitaciones & Mejoras Futuras

### Limitaciones Actuales
- Sin autenticación (añadir JWT)
- Sin rate limiting (añadir slowapi)
- Sin caché (añadir Redis)
- Logs locales solo (centralizar con ELK/Datadog)

### Mejoras Recomendadas
- [ ] Implementar JWT + OAuth2
- [ ] Agregar rate limiting (slowapi)
- [ ] Cache con Redis
- [ ] Migraciones con Alembic
- [ ] Webhooks para eventos
- [ ] Métricas con Prometheus
- [ ] Alertas automáticas

## 🔐 Notas de Seguridad

⚠️ **Producción:**
- Cambiar `SECRET_KEY` en `.env`
- Deshabilitar `APP_DEBUG=False`
- Usar HTTPS con certificados válidos
- Restringir CORS a orígenes específicos
- Usar secretos manager (AWS Secrets Manager, etc)

## 📖 API Documentation

Accedible una vez que `docker compose up`:

- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🤝 Contribuciones

Para sugerencias de mejora:
1. Crear issue describiendo el cambio
2. Fork del proyecto
3. Crear rama `feature/xyz`
4. Commits descriptivos con Conventional Commits
5. Pull request con explicación

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

---

**Última actualización**: 2024-01-15  
**Versión**: 0.1.0  
**Desarrollador**: Backend Developer

### Links Rápidos
- 📘 [API Docs](http://localhost:8000/docs)
- 🧪 [Guía de Tests](TESTING.md)
- 📋 [Ejemplos de Consumo](EXAMPLES.md)
- 📊 [Ejemplo de Ejecución](EXECUTION_EXAMPLE.md)
- 📝 [Ejemplos de Logs](LOGS_EXAMPLE.md)
