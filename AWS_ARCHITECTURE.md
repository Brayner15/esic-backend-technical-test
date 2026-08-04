# Propuesta de Arquitectura en AWS

## Resumen

Una arquitectura **simple y enfocada** para desplegar el servicio de solicitudes institucionales en AWS usando servicios gestionados.

```
Internet → ALB → ECS Fargate → RDS PostgreSQL
                 ↓
            CloudWatch Logs
```

---

## Componentes Principales

### 1. Application Load Balancer (ALB)
**¿Qué es?** Distribuidor de tráfico que enruta las peticiones HTTP/HTTPS.

**Configuración:**
- Puerto 443 (HTTPS) → Backend puerto 8000
- Certificado SSL/TLS desde AWS Certificate Manager (gratuito)
- Health checks cada 30 segundos a `/health/ready`

**Costo:** ~$16/mes (fixed) + $0.006/LCU

---

### 2. Amazon ECS Fargate
**¿Qué es?** Servicio para ejecutar contenedores sin gestionar servidores.

**Configuración:**
```
- Cluster: esic-backend-prod
- Tarea: 1 contenedor backend
  - CPU: 256 (0.25 vCPU)
  - Memory: 512 MB
  - Imagen: tu-cuenta.dkr.ecr.us-east-1.amazonaws.com/esic-backend:latest
  
- Servicio: 2 tareas (mínimo para HA)
- Auto-scaling: 2-4 tareas según CPU (70%)
- Región: us-east-1 (multi-AZ automático)
```

**Ventajas:**
- Sin gestión de servidores EC2
- Escalado automático
- Alta disponibilidad automática

**Costo:** ~$0.042/hora/tarea = ~$30/mes (2 tareas)

---

### 3. Amazon RDS PostgreSQL
**¿Qué es?** Base de datos relacional gestionada.

**Configuración:**
```
- Engine: PostgreSQL 15
- Instance: db.t3.micro (bueno para inicio)
- Storage: 20 GB SSD, auto-scaling hasta 100 GB
- Multi-AZ: Habilitado (failover automático < 2 min)
- Backups: Automáticos (7 días de retención)
- Acceso: Solo desde Security Group del backend
```

**Ventajas:**
- Backups automáticos
- Failover automático
- Patches automáticos

**Costo:** ~$60/mes (db.t3.small con Multi-AZ)

---

### 4. CloudWatch Logs
**¿Qué es?** Servicio para centralizar y analizar logs.

**Configuración:**
```
- Log Group: /ecs/esic-backend
- Retención: 30 días
- Flujo: ECS → CloudWatch automáticamente
```

**Queries útiles:**
```
# Ver errores
fields @timestamp, @message | filter @message like /ERROR/

# Latencia promedio
stats avg(duration_ms) by request_path

# Contar por status code
stats count() by status_code
```

**Costo:** ~$5/mes (logs)

---

### 5. IAM Roles (Seguridad)
**¿Qué es?** Control de permisos para cada servicio.

**Configuración:**

**ECS Task Execution Role:**
- Permisos para descargar imagen desde ECR
- Permisos para escribir logs en CloudWatch
- Permisos para leer secretos (si usas Secrets Manager)

**Application Role (en el contenedor):**
- Solo acceso a RDS
- Nada más

**Principio:** Least privilege - cada servicio solo accede a lo que necesita.

---

## Diagrama de Servicios AWS

```
                           AWS Account (us-east-1)
                           
    ┌──────────────────────────────────────────────────────────┐
    │                                                            │
    │  ┌─────────────────────────────────────────────────────┐  │
    │  │              AWS Certificate Manager               │  │
    │  │         (SSL/TLS Certificate - Gratuito)           │  │
    │  └─────────────────────────────────────────────────────┘  │
    │                          │                                 │
    │                          ▼                                 │
    │  ┌─────────────────────────────────────────────────────┐  │
    │  │   Application Load Balancer (ALB)                  │  │
    │  │   • Puerto 443 (HTTPS)                             │  │
    │  │   • Health Checks → /health/ready                  │  │
    │  │   • Distribuye traffic entre tareas                │  │
    │  │   • Multi-AZ (automático)                          │  │
    │  └─────────────────────────────────────────────────────┘  │
    │                          │                                 │
    │                          ▼                                 │
    │  ┌─────────────────────────────────────────────────────┐  │
    │  │            ECS Cluster (esic-backend-prod)         │  │
    │  │  ┌────────────────┐  ┌────────────────┐            │  │
    │  │  │   ECS Task 1   │  │   ECS Task 2   │ ← +2-4    │  │
    │  │  │ (Backend API)  │  │ (Backend API)  │   tareas  │  │
    │  │  │ CPU: 256       │  │ CPU: 256       │   según   │  │
    │  │  │ Mem: 512MB     │  │ Mem: 512MB     │   CPU     │  │
    │  │  └────────────────┘  └────────────────┘            │  │
    │  │       ↓                                              │  │
    │  │  • Containerizado (Docker)                          │  │
    │  │  • Multi-AZ automático                              │  │
    │  │  • Auto-scaling en CPU (70%)                        │  │
    │  └─────────────────────────────────────────────────────┘  │
    │                          │                                 │
    │                          ▼                                 │
    │  ┌─────────────────────────────────────────────────────┐  │
    │  │   RDS PostgreSQL (Multi-AZ)                         │  │
    │  │   • db.t3.small (2 vCPU, 2GB RAM)                  │  │
    │  │   • Storage: 20 GB (auto-scaling)                  │  │
    │  │   • Primary AZ: us-east-1a                         │  │
    │  │   • Standby AZ: us-east-1b (failover)              │  │
    │  │   • Backups: Automáticos (7 días)                  │  │
    │  └─────────────────────────────────────────────────────┘  │
    │                          │                                 │
    │                          ▼                                 │
    │  ┌─────────────────────────────────────────────────────┐  │
    │  │          CloudWatch Logs                            │  │
    │  │  • Log Group: /ecs/esic-backend                    │  │
    │  │  • Retención: 30 días                               │  │
    │  │  • JSON format (correlation IDs)                    │  │
    │  │  • Queries para debugging                           │  │
    │  └─────────────────────────────────────────────────────┘  │
    │                                                            │
    │  ┌─────────────────────────────────────────────────────┐  │
    │  │          IAM Roles & Policies                       │  │
    │  │  • ECS Task Execution Role                          │  │
    │  │  • Application Role (RDS access only)               │  │
    │  │  • Least privilege principle                        │  │
    │  └─────────────────────────────────────────────────────┘  │
    │                                                            │
    └──────────────────────────────────────────────────────────┘

    Seguridad:
    ─────────
    • ALB: Acepta HTTPS desde Internet (0.0.0.0/0)
    • Backend: Solo acepta traffic desde ALB
    • RDS: Solo acepta conexiones desde Backend
    • Encriptación en tránsito: ALB ↔ Backend
    • Encriptación en reposo: RDS
```

---

## Flujo de Petición

```
Cliente                AWS                         Backend Interno
  │                     │                                  │
  │─ HTTPS GET ────────→│                                  │
  │                     │ (Certificate Manager)             │
  │                     │ (ALB verifica SSL)                │
  │                     │                                  │
  │                     │─ HTTP POST ────────────────→    │
  │                     │ /solicitudes/                │    │
  │                     │ (Red privada)                │    │
  │                     │                              │    │
  │                     │                         (Query a RDS)
  │                     │                         (CloudWatch log)
  │                     │                              │    │
  │                     │← JSON 201 ←─────────────────│    │
  │                     │ (response)                   │    │
  │                     │                              │    │
  │← JSON 201 ──────────│                              │    │
  │ (HTTPS response)    │                              │    │
  │                     │                              │    │
```

---

## Diagrama Simple

```
┌─────────────┐
│   Internet  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  ALB (HTTPS:443)        │
│  Health checks → /health/ready
└──────┬──────────────────┘
       │
       ▼ (HTTP:8000)
┌─────────────────────────┐
│  ECS Fargate            │
│  - 2-4 tareas           │
│  - Auto-scaling en CPU  │
│  - Multi-AZ automático  │
└──────┬──────────────────┘
       │
       ▼ (Puerto 5432)
┌─────────────────────────┐
│  RDS PostgreSQL         │
│  - Multi-AZ             │
│  - Backups automáticos  │
│  - Failover < 2 min     │
└─────────────────────────┘
       ▲
       │
       └── CloudWatch Logs (JSON)
```

---

## Flujo de una Solicitud

1. **Usuario envía petición** → `POST /solicitudes/`
2. **ALB recibe** → Verifica certificado SSL
3. **ALB enruta** → A una tarea ECS (distribuida)
4. **Backend procesa** → Valida datos, consulta BD
5. **RDS retorna** → Datos de la solicitud
6. **Backend responde** → 201 Created
7. **Logs se escriben** → CloudWatch automáticamente

---

## Escalado Automático

```
CPU < 30% → Reduce de 4 a 2 tareas (ahorro de costos)
CPU 30-70% → Mantiene 2 tareas (normal)
CPU > 70% → Aumenta a 3-4 tareas (carga alta)
```

**Tiempo de escalado:** ~2-3 minutos

---

## Alta Disponibilidad

**Si una tarea falla:**
- ALB detecta (health check falla)
- ECS lanza nueva tarea automáticamente
- Tiempo de recuperación: ~1-2 minutos

**Si una AZ cae (datacenter):**
- RDS failover automático a otra AZ (~30 segundos)
- ECS tareas se lanzan en otra AZ
- Tiempo total de recuperación: ~2 minutos

---

## Costo Estimado Mensual

| Servicio | Cantidad | Costo |
|----------|----------|-------|
| ALB | 1 | $16 |
| ECS Fargate | 2-4 tareas | $30-60 |
| RDS PostgreSQL | db.t3.small Multi-AZ | $60 |
| CloudWatch | Logs | $5 |
| Data Transfer | ~100GB | $5 |
| **TOTAL** | | **~$116-146/mes** |

---

## Pasos para Desplegar

### 1. Preparar Imagen Docker
```bash
# Construir y subir a ECR
aws ecr get-login-password | docker login --username AWS --password-stdin 123456.dkr.ecr.us-east-1.amazonaws.com
docker build -t esic-backend .
docker tag esic-backend:latest 123456.dkr.ecr.us-east-1.amazonaws.com/esic-backend:latest
docker push 123456.dkr.ecr.us-east-1.amazonaws.com/esic-backend:latest
```

### 2. Crear Cluster ECS
```bash
# Usar consola AWS o CLI
aws ecs create-cluster --cluster-name esic-backend-prod
```

### 3. Crear RDS PostgreSQL
```bash
# Consola AWS o CLI
aws rds create-db-instance \
  --db-instance-identifier esic-db \
  --db-instance-class db.t3.small \
  --engine postgres \
  --master-username admin \
  --master-user-password <contraseña-fuerte> \
  --multi-az
```

### 4. Crear ALB
```bash
# Consola AWS → EC2 → Load Balancers
# Crear ALB, target group, listener HTTPS
```

### 5. Crear Servicio ECS
```bash
# Consola AWS o CLI
# Definir task definition + servicio + auto-scaling
```

---

## Monitoreo

**Métricas a vigilar:**
```
- CPU% del contenedor (target: < 70%)
- Memoria% (target: < 80%)
- Error rate (% de 5xx errors)
- Request latency (p95, p99)
- RDS connections activas
```

**Alertas recomendadas:**
```
- CPU > 80% por 5 min → Escalar
- Error rate > 5% → Notificar
- RDS connections > 80% → Investigar
```

---

## Seguridad

**Security Groups:**
```
ALB: Permite tráfico 443 desde 0.0.0.0/0
Backend: Permite 8000 solo desde ALB
RDS: Permite 5432 solo desde Backend
```

**Secretos:**
- DATABASE_PASSWORD en AWS Secrets Manager (no en código)
- Rotación automática cada 90 días

**SSL/TLS:**
- ALB termina HTTPS
- Comunicación ALB→Backend en HTTP (red privada)
- Comunicación Backend→RDS encriptada

---

## Limitaciones y Mejoras Futuras

**Limitaciones actuales:**
- Single region (no multi-region)
- Sin caché (Redis)
- Sin CDN (CloudFront)

**Mejoras futuras:**
- Agregar ElastiCache (Redis) para caché
- CloudFront para static assets (si aplica)
- AWS WAF para protección adicional
- Multi-region para DR (Disaster Recovery)

---

## Conclusión

Esta arquitectura proporciona:
- ✅ **Alta disponibilidad** (Multi-AZ, auto-scaling)
- ✅ **Bajo mantenimiento** (servicios gestionados)
- ✅ **Costo controlado** (~$120/mes)
- ✅ **Escalabilidad** (automática según carga)
- ✅ **Seguridad** (IAM, Security Groups, SSL/TLS)

Es ideal para empezar en producción sin complejidad innecesaria.
