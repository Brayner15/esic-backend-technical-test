# Integración del Servicio ESIC en Ecosistema Multi-Servicio

## Resumen Ejecutivo

El servicio de solicitudes institucionales (ESIC) se integra como un microservicio independiente dentro de una arquitectura de API Gateway compartida. La solución utiliza autenticación basada en tokens JWT, gestión centralizada de secretos, y observabilidad distribuida para garantizar trazabilidad y seguridad en un entorno multi-tenant.

---

## 1. Flujograma de Integración

```
┌─────────────────────────────────────────────────────────────────┐
│                           USUARIO                               │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS Request
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (SPA/Web)                           │
│  • React/Vue/Angular                                            │
│  • Almacena JWT Token en memoria/localStorage                   │
│  • Rutas de solicitudes: /solicitudes/*                         │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS + JWT Token en header
                         │ POST/GET/PUT /api/v1/solicitudes
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DNS / Route 53                               │
│  • api.institucion.com → CloudFront/WAF endpoint                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              AWS WAF + CloudFront                               │
│  • Rate limiting: 1000 req/5min por IP                          │
│  • Detección de ataques DDoS                                    │
│  • Caché de respuestas estáticas                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           API Gateway + Load Balancer                           │
│  • Validación de JWT Token                                      │
│  • Rate limiting: 10,000 req/día por usuario                    │
│  • Enrutamiento por path:                                       │
│    ├─ /api/v1/solicitudes → ESIC Service                        │
│    ├─ /api/v1/usuarios → Usuario Service                        │
│    ├─ /api/v1/notificaciones → Notificación Service             │
│    └─ /api/v1/reportes → Reporte Service                        │
│  • Logging de todos los requests (CloudWatch)                   │
└──────────────┬──────────────────────┬──────────────────┬────────┘
               │                      │                  │
      ESIC     │                      │   Otros          │
      Service  │ Usuarios Service     │   Servicios      │
               │                      │                  │
               ▼                      ▼                  ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   ECS Fargate        │  │   ECS Fargate    │  │   ECS Fargate    │
│   ESIC Backend       │  │   Usuario Svc    │  │   Otros Servicios│
│  • 2-4 tareas       │  │  • 1-2 tareas   │  │  • N tareas      │
│  • Auto-scaling      │  │  • Auto-scaling  │  │  • Auto-scaling  │
│  • Multi-AZ          │  │  • Multi-AZ      │  │  • Multi-AZ      │
│  • 256 CPU, 512 MB   │  │  • Similar setup │  │  • Similar setup │
└──────────┬───────────┘  └────────┬─────────┘  └────────┬─────────┘
           │                       │                     │
           │   Shared DB Schema    │                     │
           └───────────┬───────────┴─────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   RDS PostgreSQL (Multi-AZ, Private) │
        │  • Master DB: esic_prod              │
        │  • Schemas separados por servicio    │
        │  • Read replicas para reportes       │
        │  • Backups automáticos (7 días)      │
        │  • Encriptación en reposo            │
        └──────────────────────────────────────┘
               ▲           ▲                ▲
               │           │                │
               │ (Queries)  │ (Events)       │ (Replication)
               │           │                │
        ┌──────┴────────────┴────────────────┴──────────────┐
        │                                                    │
        ▼                                    ▼               ▼
┌──────────────────────────────┐  ┌──────────────────┐
│   Secrets Manager            │  │   Event Bridge   │
│  • DB Passwords              │  │  • Eventos de    │
│  • API Keys                  │  │    solicitudes   │
│  • JWT Secret Key            │  │  • Notificaciones│
│  • Rotación automática       │  │  • Auditoría     │
│  • Acceso via IAM            │  └──────────────────┘
└──────────────────────────────┘
               ▲
               │
┌──────────────┴────────────────────────────────────────────┐
│                                                            │
│         OBSERVABILIDAD Y SEGURIDAD                         │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ CloudWatch Logs (Centralizado)                       │ │
│  │ • /ecs/esic-backend (logs aplicación)                │ │
│  │ • /aws/apigateway/* (logs de API)                    │ │
│  │ • /aws/rds/* (logs de BD)                            │ │
│  │ • Retention: 30-90 días                              │ │
│  │ • Correlation ID: Trazabilidad end-to-end            │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ CloudWatch Metrics + Dashboards                      │ │
│  │ • Latencia de requests (p50, p95, p99)               │ │
│  │ • Error rate por servicio                            │ │
│  │ • CPU/Memoria de tareas ECS                          │ │
│  │ • Conexiones activas a RDS                           │ │
│  │ • Custom metrics desde aplicación                    │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ CloudTrail + GuardDuty + Security Hub                │ │
│  │ • Auditoría de cambios en infraestructura             │ │
│  │ • Detección de comportamientos anómalos              │ │
│  │ • Alertas de seguridad centralizadas                 │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 2. Flujo de una Solicitud (ESIC)

```
Cliente → Frontend
   │
   └─ POST /api/v1/solicitudes/ + JWT Token
      └─ API Gateway (valida JWT, rate limit)
         └─ ALB (distribuye carga)
            └─ ECS Task ESIC (procesa solicitud)
               ├─ Valida datos
               ├─ Consulta RDS
               ├─ Emite evento a EventBridge
               ├─ Registra log en CloudWatch
               └─ Retorna 201 Created
      └─ EventBridge (propaga eventos)
         ├─ Notificación Service (envía email)
         ├─ Reporte Service (actualiza analytics)
         └─ Auditoría (registra cambio)
      └─ Cliente recibe response
```

---

## 3. Componentes Clave de Integración

### A. **Autenticación y Autorización**
- **JWT Tokens**: Emitidos por Auth Service centralizado
- **Header Authorization**: `Authorization: Bearer <token>`
- **Validación**: API Gateway valida antes de enrutar
- **Alcance**: ESIC tiene scope `solicitudes:read`, `solicitudes:write`
- **Expiración**: 1 hora (refresh tokens 7 días)

### B. **Gestión de Secretos**
- **Database Credentials**: AWS Secrets Manager
- **Rotación**: Automática cada 90 días
- **Acceso**: Solo IAM roles autorizadas (ECS Task Role)
- **Encriptación**: KMS CMK por entorno (dev/staging/prod)

### C. **Logs Distribuidos y Trazabilidad**
- **Correlation ID**: Generado en API Gateway, propagado en headers
- **Format JSON**: Estructurado para análisis
- **Campos obligatorios**:
  - `@timestamp`, `correlation_id`, `user_id`, `request_path`
  - `duration_ms`, `status_code`, `service_name`
- **Retention**: Dev 7 días, Staging 30 días, Prod 90 días

### D. **Métricas y Alertas**
- **Métricas por servicio**: CPU, memoria, latencia, errores
- **Alertas SNS**: Email/Slack si error rate > 5% o latencia p99 > 2s
- **Dashboard centralizado**: CloudWatch + Grafana
- **SLA Monitoring**: Uptime target 99.9% (43.2 min/mes)

### E. **Seguridad y Compliance**
- **Network**: VPC privada, sin acceso directo a Internet
- **Data**: Encriptación en tránsito (TLS) y en reposo (KMS)
- **IAM**: Least privilege por servicio
- **Auditoría**: CloudTrail registra todas las API calls

---

## 4. Configuración de Deployment

```yaml
# docker-compose-prod.yml (para referencia)
version: '3.8'
services:
  esic-backend:
    image: ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/esic-backend:${VERSION}
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/esic_prod
      - JWT_SECRET=${JWT_SECRET}  # De Secrets Manager
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - CORRELATION_ID_HEADER=X-Correlation-ID
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    networks:
      - backend-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 5. Procedimiento de Integración

1. **Crear Task Definition en ECS** con imagen del servicio ESIC
2. **Registrar ruta en API Gateway**: `/api/v1/solicitudes*` → ESIC Target Group
3. **Configurar IAM Role**: Permisos a RDS, Secrets Manager, CloudWatch
4. **Setup CloudWatch Logs**: Group `/ecs/esic-backend` con formato JSON
5. **Crear dashboards**: Latencia, errores, concurrencia
6. **Definir alertas**: Email/Slack para anomalías
7. **Test end-to-end**: Validar flujo completo con datos reales
8. **Canary Deployment**: 5% tráfico → 50% → 100% en 24-48h

---

## 6. Consideraciones de Escalabilidad

| Métrica | Límite Actual | Escalabilidad |
|---------|---------------|--------------|
| Requests/seg | ~50 (2-4 tareas) | +Horizontal (más tareas) |
| DB Connections | ~20/tarea | +Read replicas, caché |
| Storage | 20-100 GB | +Auto-scaling RDS |
| Usuarios concurrentes | ~5000 | +API Gateway throttling |

---

## Conclusión

El servicio ESIC se integra de manera segura y escalable como un microservicio dentro del ecosistema existente. La arquitectura garantiza:
- ✅ **Seguridad**: JWT, encriptación, IAM roles
- ✅ **Confiabilidad**: Multi-AZ, failover automático
- ✅ **Observabilidad**: Logs centralizados, trazabilidad end-to-end
- ✅ **Escalabilidad**: Auto-scaling horizontal y vertical
- ✅ **Mantenibilidad**: Servicios gestionados, mínima intervención
