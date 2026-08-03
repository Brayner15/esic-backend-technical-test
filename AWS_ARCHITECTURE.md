# Propuesta de Arquitectura en AWS

## Resumen Ejecutivo

Esta propuesta describe el despliegue de un servicio backend de gestión de solicitudes institucionales en AWS, manteniendo alta disponibilidad, escalabilidad y seguridad. La solución utiliza servicios gestionados de AWS para minimizar overhead operacional y maximizar confiabilidad.

**Componentes Clave:**
- Application Load Balancer (ALB) para enrutamiento inteligente
- Amazon ECS (Fargate) para containers sin servidor
- Amazon RDS PostgreSQL para base de datos relacional
- AWS Secrets Manager para gestión de credenciales
- Amazon CloudWatch para logging y monitoreo
- AWS WAF para protección contra tráfico malicioso

---

## 1. Arquitectura de Red

### VPC y Subnets

```
AWS Account (us-east-1)
│
├─ VPC (10.0.0.0/16)
│  │
│  ├─ Public Subnets (ALB, NAT Gateway)
│  │  ├─ AZ-1a: 10.0.1.0/24
│  │  └─ AZ-1b: 10.0.2.0/24
│  │
│  ├─ Private Subnets (ECS Tasks, RDS)
│  │  ├─ AZ-1a: 10.0.10.0/24
│  │  └─ AZ-1b: 10.0.11.0/24
│  │
│  └─ Isolated Subnets (RDS only, no internet access)
│     ├─ AZ-1a: 10.0.20.0/24
│     └─ AZ-1b: 10.0.21.0/24
│
├─ Internet Gateway (para tráfico público)
├─ NAT Gateway (acceso a internet desde privadas)
└─ VPC Endpoints (acceso a servicios AWS sin internet)
```

**Justificación:**
- **Alta Disponibilidad:** Multi-AZ en 2+ zonas de disponibilidad
- **Seguridad en Capas:** Separación entre públicas y privadas
- **RDS Aislada:** Base de datos sin acceso directo a internet
- **Escalabilidad:** Subnets con espacio para crecimiento

### Security Groups

```
ALB Security Group (sg-alb)
├─ Ingress:
│  ├─ Port 80 (HTTP) from 0.0.0.0/0
│  ├─ Port 443 (HTTPS) from 0.0.0.0/0
│  └─ Port 8001 (External Service) from 0.0.0.0/0
└─ Egress: All traffic to Backend SG

Backend Security Group (sg-backend)
├─ Ingress:
│  ├─ Port 8000 from ALB SG
│  └─ Port 8001 from ALB SG
├─ Egress:
│  ├─ Port 5432 (PostgreSQL) to RDS SG
│  └─ Port 443 to 0.0.0.0/0 (HTTPS para APIs externas)
└─ Self-referencing para inter-task communication

RDS Security Group (sg-rds)
├─ Ingress: Port 5432 from Backend SG only
└─ Egress: None (RDS es destino)
```

---

## 2. Componentes de Compute

### Amazon ECS (Elastic Container Service) - Fargate

**Backend Service:**
- **Cluster:** `esic-backend-prod`
- **Task Definition:** `esic-backend-task`
  - CPU: 512 (0.5 vCPU)
  - Memory: 1024 MB (1 GB)
  - Containers: 2 (backend + sidecar logging)
  - Image: `<account-id>.dkr.ecr.us-east-1.amazonaws.com/esic-backend:latest`

**Consumer Service:**
- **Type:** Scheduled Task (ECS Scheduled Rules)
- **Schedule:** Cron `0 */6 * * ?` (cada 6 horas)
- **Task Definition:** `esic-consumer-task`
  - CPU: 256 (0.25 vCPU)
  - Memory: 512 MB
  - Image: `<account-id>.dkr.ecr.us-east-1.amazonaws.com/esic-consumer:latest`

**Service Configuration:**
```
Service Name: esic-backend-service
Desired Count: 2 (mínimo para HA)
Deployment Configuration:
  - Minimum: 100% (al menos 1 task corriendo)
  - Maximum: 200% (hasta 4 tasks durante updates)
Auto Scaling:
  - Min: 2 tasks
  - Max: 10 tasks
  - Target CPU: 70%
  - Target Memory: 80%
```

**Ventajas de Fargate:**
- ✅ Sin gestión de instancias EC2
- ✅ Escalado automático
- ✅ Pricing por uso real
- ✅ Integración nativa con CloudWatch

### External Container Registry

**Amazon ECR (Elastic Container Registry):**
```
Repositories:
├─ esic-backend
│  ├─ latest (última imagen)
│  ├─ v0.1.0 (releases)
│  └─ <commit-sha> (todas las builds)
├─ esic-consumer
└─ esic-external-service

Image Scanning:
├─ Enabled: Scan on push
├─ Auto-delete: Imágenes viejas > 30 días
└─ Notifications: SNS para vulnerabilidades
```

---

## 3. Base de Datos

### Amazon RDS PostgreSQL

**Configuración:**
```
Engine: PostgreSQL 15.2
Instance Class: db.t3.small (2 vCPU, 2 GB RAM)
Storage:
  - Type: gp3 (SSD)
  - Size: 100 GB inicial
  - Auto-scaling: Hasta 500 GB
  - Backups: Automáticos cada 6 horas
  - Retention: 30 días

Multi-AZ:
  - Enabled: Standby en AZ diferente
  - Failover: Automático < 2 minutos
  - RTO: < 5 minutos
  - RPO: < 1 minuto

Performance Insights:
  - Enabled: Monitoreo de rendimiento
  - Retention: 7 días
```

**Acceso:**
- Endpoint privado solo dentro de VPC
- No tiene IP pública
- Accesible solo desde Backend SG

**Backups y Disaster Recovery:**
```
Snapshots automáticos: Diarios
AWS Backup Integration: Retenidos 90 días
Cross-Region Backup: Copia en us-west-2
RTO: < 5 minutos (restore desde snapshot)
RPO: < 1 hora (último backup)
```

---

## 4. Load Balancing y Routing

### Application Load Balancer (ALB)

**Configuración:**
```
Name: esic-alb
Scheme: Internet-facing
IP Address Type: IPv4
Subnets: Public subnets en AZ-1a y AZ-1b

Listeners:
├─ HTTP (80) → Redirect to HTTPS
└─ HTTPS (443)
   └─ Rules:
      ├─ /solicitudes/* → Backend Target Group
      ├─ /health* → Backend Target Group
      └─ /* → 404 Not Found
```

**Target Groups:**

```
Target Group 1: esic-backend-tg
├─ Protocol: HTTP
├─ Port: 8000
├─ Health Check:
│  ├─ Path: /health/ready
│  ├─ Protocol: HTTP
│  ├─ Interval: 30s
│  ├─ Timeout: 5s
│  ├─ Healthy threshold: 2
│  ├─ Unhealthy threshold: 2
│  └─ Success codes: 200
├─ Stickiness:
│  ├─ Enabled: No (stateless)
│  └─ Duration: N/A
└─ Type: IP (para Fargate tasks)

Target Group 2: esic-external-service-tg
├─ Protocol: HTTP
├─ Port: 8001
└─ Similar health check
```

**SSL/TLS:**
```
Certificate: AWS Certificate Manager
Domain: api.esic.example.com
Auto-renewal: Habilitado
Minimum TLS Version: 1.2
Cipher Suites: Modernas
```

---

## 5. Seguridad y Compliance

### AWS WAF (Web Application Firewall)

```
Asociado a: ALB
Rules:
├─ AWS Managed Rules
│  ├─ Core Rule Set (protección general)
│  ├─ Known Bad Inputs
│  └─ SQL Injection
├─ Rate Limiting
│  └─ 2000 requests por 5 minutos por IP
├─ IP Reputation Lists
│  └─ Bloquear IPs maliciosas conocidas
└─ Custom Rules
   ├─ Bloquear payloads > 1MB
   └─ Validar Content-Type
```

### Secrets Management

```
AWS Secrets Manager:
├─ /esic/rds/master
│  ├─ username: esic_admin
│  ├─ password: <random-64-chars>
│  └─ Rotation: 90 días
├─ /esic/app/secret-key
│  └─ Rotation: 180 días
├─ /esic/external-api/key
│  └─ Rotation: As needed
└─ Versioning: Mantener últimas 3 versiones
```

### IAM Roles y Policies

```
ECS Task Execution Role:
├─ AmazonECSTaskExecutionRolePolicy (AWS managed)
├─ CloudWatch Logs (logs:CreateLogGroup, logs:PutLogEvents)
├─ ECR (ecr:GetAuthorizationToken)
├─ Secrets Manager (secretsmanager:GetSecretValue)
└─ X-Ray (xray:PutTraceSegments)

Application Role:
├─ RDS database connect
├─ S3 access (si hay uploads)
├─ SNS publish (para eventos)
└─ Deny all other services (least privilege)
```

### Encryption

```
At-Rest:
├─ RDS: KMS encryption
├─ EBS: Encrypted volumes
├─ S3: Server-side encryption (si aplica)
└─ Secrets Manager: AWS managed key

In-Transit:
├─ ALB to ECS: TLS 1.2+
├─ ECS to RDS: Encrypted connection string
└─ Client to ALB: HTTPS (HTTP redirect)
```

---

## 6. Logging, Monitoring y Alertas

### CloudWatch Logs

```
Log Groups:
├─ /ecs/esic-backend/
│  └─ Log Streams:
│     ├─ esic-backend-service/backend/<task-id>
│     ├─ esic-backend-service/sidecar/<task-id>
│     └─ Consumer runs
│
└─ Retention: 30 días (configurable)

Log Format: JSON (correlation IDs, timestamps, levels)

Insights Queries:
├─ fields @timestamp, @message, correlation_id
├─ stats count() by status_code
├─ stats avg(duration_ms) by request_path
└─ filter @message like /ERROR/
```

### CloudWatch Metrics

```
Custom Metrics:
├─ RequestCount (por status code)
├─ ResponseTime (p50, p95, p99)
├─ ErrorRate (5xx errors)
├─ DuplicateRequestsDetected
└─ ConsumerSuccess Rate

Built-in Metrics:
├─ ECS: CPU, Memory, Task Count
├─ RDS: CPU, Connections, Query Latency
├─ ALB: Request Count, Target Health
└─ Network: In/Out bytes
```

### CloudWatch Alarms

```
Critical Alarms:
├─ AlarmName: esic-backend-high-error-rate
│  └─ Threshold: > 5% de 5xx errors en 5 min
├─ AlarmName: esic-rds-connection-exceeded
│  └─ Threshold: > 80% de max connections
├─ AlarmName: esic-alb-unhealthy-targets
│  └─ Threshold: Cualquier target unhealthy
└─ AlarmName: esic-duplicate-external-id-spike
   └─ Threshold: > 10 duplicados en 1 minuto

Actions:
├─ SNS Topic: esic-alerts
├─ Email notifications
├─ PagerDuty integration (opcional)
└─ Auto-remediation: Lambda triggers
```

### X-Ray Tracing

```
Enabled en:
├─ ALB (AWS SDK instrumentation)
├─ ECS tasks (sidecar agent)
└─ RDS connections

Captures:
├─ Request lifecycle
├─ Latency per component
├─ Error traces
└─ Database query performance
```

---

## 7. CI/CD Pipeline

### AWS CodePipeline

```
Pipeline: esic-backend-pipeline

Stage 1: Source
└─ GitHub (Trigger en push a main)

Stage 2: Build
├─ CodeBuild Project: esic-backend-build
│  ├─ Environment: Python 3.10
│  ├─ Steps:
│  │  ├─ pip install requirements
│  │  ├─ pytest tests/ --cov
│  │  ├─ docker build
│  │  └─ docker push to ECR
│  └─ Artifacts: Build logs

Stage 3: Deploy
├─ CodeDeploy to ECS
├─ Deployment Type: Rolling
│  ├─ Min: 100% healthy
│  ├─ Max: 200% capacity
│  └─ Wait time: 5 min between batches
└─ Rollback: Automático on failure

Approval Gates:
└─ Manual approval antes de producción
```

### Deployment Strategy

```
Rolling Deployment:
├─ Deploy to 50% of tasks
├─ Verify health checks
├─ Deploy to remaining 50%
├─ Total time: ~5-10 minutos
└─ Rollback: Automático si algún task falla

Canary Deployment (Opcional):
├─ Deploy a 10% de traffic
├─ Monitor metrics por 5 min
├─ Increase to 100%
├─ Rollback si errores > 1%
└─ Time: ~15-20 minutos
```

---

## 8. Escalabilidad y Performance

### Auto Scaling

```
Target Tracking Scaling Policy:
├─ Metric: Average CPU Utilization
├─ Target: 70%
├─ Scale-out: +2 tasks when > 70%
├─ Scale-in: -1 task when < 30% (delay 5 min)
├─ Min: 2 tasks
├─ Max: 10 tasks
└─ Cooldown: 300 segundos

Step Scaling (Opcional):
├─ Agresivo scale-out on memory alerts
├─ Conservative scale-in
└─ Prevents thrashing
```

### RDS Scaling

```
Read Replicas:
├─ Region: us-east-1 (mismo)
├─ Count: 1-2 read replicas
├─ Use case: Reportes, consumer queries
├─ Connection pool: 10 connections per replica

Vertical Scaling (Manual):
├─ Monitor: CloudWatch Performance Insights
├─ Upgrade path: t3.small → t3.medium → t3.large
└─ Downtime: < 1 minuto (multi-AZ)
```

---

## 9. Disaster Recovery

### Backup Strategy

```
Snapshots RDS:
├─ Manual: Post-deployment
├─ Automated: Diarios a las 02:00 UTC
├─ Retention: 30 días
└─ Cross-region copy: Semanal a us-west-2

ECR Images:
├─ Retain: Últimas 20 builds
├─ Tag pattern: v0.1.0, v0.2.0, latest
└─ Lifecycle: Auto-delete old images

CloudFormation Templates:
├─ Infrastructure as Code
├─ Version control
└─ Rollback capability
```

### Recovery Time Objectives (RTO)

```
Database Failure:
├─ RDS Multi-AZ failover: < 2 minutos
├─ Manual restore from snapshot: < 10 minutos

Application Failure:
├─ Health check detection: < 30 segundos
├─ Auto-scale new tasks: < 2 minutos
├─ Total: < 3 minutos

Region Failure:
├─ Failover to us-west-2: < 30 minutos
└─ Requires manual intervention
```

---

## 10. Estimación de Costos

### Breakdown Mensual (Estimado)

| Componente | Precio/mes | Notas |
|-----------|-----------|-------|
| ECS Fargate | $30-50 | 2-4 tasks, 512 CPU |
| RDS PostgreSQL | $40-60 | db.t3.small, 100 GB |
| ALB | $15-20 | Includes 50 GB data |
| NAT Gateway | $30-40 | High traffic |
| CloudWatch | $5-10 | Logs, metrics, alarms |
| Secrets Manager | $0.40 | 1 secret |
| Bandwidth | $10-20 | Egress charges |
| **Total** | **$130-200** | Por mes |

**Optimizaciones:**
- Reserved Instances: -30% en RDS
- Savings Plans: -20% en ECS
- Consolidar en 1 AZ dev: -50%

---

## 11. Decisiones de Arquitectura

| Decision | Rationale |
|----------|-----------|
| **Fargate vs EC2** | Managed service, menos overhead operacional |
| **Multi-AZ** | Alta disponibilidad, comply con SLAs |
| **RDS vs Self-managed** | Backups, failover, patching automáticos |
| **ALB vs API Gateway** | Better para containers, WebSocket support |
| **WAF habilitado** | Protección contra ataques OWASP top 10 |
| **Secrets Manager** | Rotation automática, audit trail |
| **CloudWatch vs ELK** | AWS native, integración tighter |
| **No usar Lambda** | Containers más simples para migraciones futuras |

---

## 12. Matriz de Responsabilidades (AWS vs Aplicación)

| Componente | AWS Responsibility | App Responsibility |
|-----------|-------------------|-------------------|
| **Containers** | Orchestration, Scaling | Image building, Dockerfile |
| **Database** | Availability, Backups, Patching | Schema design, Queries |
| **Network** | VPC, Security Groups, Routing | Connection strings, Timeouts |
| **Security** | Infrastructure encryption, IAM | Application-level auth, validation |
| **Logging** | Log storage, retention, Insights | Structured logging format |
| **Monitoring** | Infrastructure metrics | Business logic metrics |

---

## Conclusión

Esta arquitectura proporciona:
- ✅ **Disponibilidad 99.9%** (SLA estándar AWS)
- ✅ **Escalabilidad automática** (2-10 tasks)
- ✅ **Seguridad en capas** (WAF, VPC, Encryption)
- ✅ **Observabilidad completa** (Logs, Metrics, Traces)
- ✅ **Disaster Recovery** (Backups, failover automático)
- ✅ **Costo controlado** ($130-200/mes)

**Siguiente paso:** Implementar con CloudFormation o Terraform.
