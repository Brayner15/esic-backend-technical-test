# Flujograma de Arquitectura AWS

## Diagrama General de Componentes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          INTERNET / USUARIOS                             │
│                                                                           │
│                          HTTPS Traffic                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                 ↓
                    ┌────────────────────────┐
                    │    AWS Route 53        │
                    │   (DNS + Health Check)  │
                    │                         │
                    │ api.esic.example.com   │
                    └────────────────────────┘
                                 ↓
              ┌──────────────────────────────────────┐
              │         AWS WAF                       │
              │  Rate Limiting, IP Filtering          │
              │  SQL Injection Protection             │
              └──────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                                VPC (10.0.0.0/16)                         │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │               Public Subnets (ALB Layer)                         │   │
│  │                                                                  │   │
│  │   ┌────────────────────────────────────────────────────────┐    │   │
│  │   │    Application Load Balancer                          │    │   │
│  │   │  - Listen 443 (HTTPS)                                 │    │   │
│  │   │  - SSL/TLS Certificate (ACM)                          │    │   │
│  │   │  - Route Rules                                        │    │   │
│  │   │                                                        │    │   │
│  │   │  Rule 1: /solicitudes/* → Backend TG                │    │   │
│  │   │  Rule 2: /health* → Backend TG                       │    │   │
│  │   │  Default: 404                                        │    │   │
│  │   └────────────────────────────────────────────────────────┘    │   │
│  │                   ↓                                              │   │
│  │   ┌──────────────────────────────┐                              │   │
│  │   │  Target Group: backend-tg    │                              │   │
│  │   │  - Port: 8000                │                              │   │
│  │   │  - Protocol: HTTP            │                              │   │
│  │   │  - Health Check: /health/ready                             │   │
│  │   │  - Healthy Threshold: 2      │                              │   │
│  │   └──────────────────────────────┘                              │   │
│  │            ↓            ↓                                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │            Private Subnets (Application Layer)                   │   │
│  │                                                                  │   │
│  │   ┌─────────────────────────┐   ┌─────────────────────────┐    │   │
│  │   │  ECS Task (AZ-1a)       │   │  ECS Task (AZ-1b)       │    │   │
│  │   │                         │   │                         │    │   │
│  │   │ Container: Backend      │   │ Container: Backend      │    │   │
│  │   │  - Port 8000            │   │  - Port 8000            │    │   │
│  │   │  - CPU: 512 (0.5 vCPU)  │   │  - CPU: 512             │    │   │
│  │   │  - Memory: 1 GB         │   │  - Memory: 1 GB         │    │   │
│  │   │                         │   │                         │    │   │
│  │   │ Container: Log Router   │   │ Container: Log Router   │    │   │
│  │   │  (Sidecar)              │   │  (Sidecar)              │    │   │
│  │   │  - CloudWatch Logs      │   │  - CloudWatch Logs      │    │   │
│  │   │  - Correlation IDs      │   │  - Correlation IDs      │    │   │
│  │   │                         │   │                         │    │   │
│  │   └──────┬──────────────────┘   └──────┬──────────────────┘    │   │
│  │          │ (Port 5432)                  │ (Port 5432)          │   │
│  │          └───────────┬──────────────────┘                      │   │
│  │                      ↓                                         │   │
│  │     ┌─────────────────────────────────────────┐               │   │
│  │     │  Private Subnets (Database Layer)       │               │   │
│  │     │                                         │               │   │
│  │     │   ┌───────────────────────────────┐    │               │   │
│  │     │   │  RDS PostgreSQL Multi-AZ      │    │               │   │
│  │     │   │                               │    │               │   │
│  │     │   │  Primary Instance (AZ-1a)    │    │               │   │
│  │     │   │  - db.t3.small                │    │               │   │
│  │     │   │  - 100 GB gp3 storage         │    │               │   │
│  │     │   │  - Encrypted with KMS         │    │               │   │
│  │     │   │  - Automated backups (daily)  │    │               │   │
│  │     │   │                               │    │               │   │
│  │     │   │  ↕ Synchronous Replication   │    │               │   │
│  │     │   │                               │    │               │   │
│  │     │   │  Standby Instance (AZ-1b)    │    │               │   │
│  │     │   │  - Warm standby               │    │               │   │
│  │     │   │  - Automatic failover < 2min │    │               │   │
│  │     │   └───────────────────────────────┘    │               │   │
│  │     │                                         │               │   │
│  │     │   Read Replicas (Optional):             │               │   │
│  │     │   - Aurora read endpoint                │               │   │
│  │     │   - For reports/analytics               │               │   │
│  │     └─────────────────────────────────────────┘               │   │
│  │                                                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │           Supporting Services (Inside VPC)                       │   │
│  │                                                                  │   │
│  │  • AWS Secrets Manager → RDS Credentials, API Keys              │   │
│  │  • VPC Endpoints → CloudWatch, S3, ECR                          │   │
│  │  • NAT Gateway → Outbound internet (ECS → External APIs)        │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                 ↓
              ┌──────────────────────────────────────┐
              │      AWS CloudWatch                   │
              │  - Logs: /ecs/esic-backend/*          │
              │  - Metrics: CPU, Memory, Requests     │
              │  - Alarms: Error rates, Health        │
              │  - X-Ray: Request tracing             │
              │  - Insights: Log queries              │
              └──────────────────────────────────────┘
                                 ↓
         ┌───────────────────────────────────────┐
         │      AWS SNS (Notifications)          │
         │                                       │
         │  esic-alerts topic                    │
         │  ↓ Email                              │
         │  ↓ PagerDuty                          │
         │  ↓ Lambda (Auto-remediation)          │
         └───────────────────────────────────────┘
```

---

## Request Lifecycle Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER REQUEST: POST /solicitudes/                  │
│                        Body: { external_id, ... }                        │
└─────────────────────────────────────────────────────────────────────────┘
                                 ↓
                        ┌─────────────────────┐
                        │   Route 53 (DNS)    │
                        │ Resolve hostname    │
                        │ → ALB endpoint      │
                        └─────────────────────┘
                                 ↓
                        ┌─────────────────────┐
                        │   Client connect    │
                        │   TLS 1.2 handshake │
                        │   Certificate check │
                        └─────────────────────┘
                                 ↓
                        ┌─────────────────────┐
                        │    AWS WAF          │
                        │ ✓ Check IP repos    │
                        │ ✓ Rate limit check  │
                        │ ✓ OWASP rules       │
                        └─────────────────────┘
                                 ↓
                  ┌──────────────────────────┐
                  │   ALB receives request   │
                  │   Create X-Correlation   │
                  │   ID (if not provided)   │
                  │   Add to request header  │
                  └──────────────────────────┘
                                 ↓
                  ┌──────────────────────────┐
                  │   ALB route decision     │
                  │   Path /solicitudes/ →   │
                  │   backend-tg             │
                  └──────────────────────────┘
                                 ↓
      ┌─────────────────────────────────────────────────┐
      │   Target Group health check                     │
      │   ✓ If healthy → forward                        │
      │   ✗ If unhealthy → 503 Service Unavailable      │
      │   ✓ Auto-deregister unhealthy targets           │
      └─────────────────────────────────────────────────┘
                                 ↓
          ┌──────────────────────────────────────┐
          │    ECS Task Selection (Round Robin)  │
          │                                      │
          │  Healthy tasks:                      │
          │  • Task 1 (AZ-1a) ← SELECT           │
          │  • Task 2 (AZ-1b)                    │
          │                                      │
          │  Forward to: 10.0.10.x:8000          │
          └──────────────────────────────────────┘
                                 ↓
          ┌──────────────────────────────────────┐
          │   FastAPI Application Handler        │
          │                                      │
          │  1. Middleware: LoggingMiddleware    │
          │     ├─ Log: request_started          │
          │     ├─ Correlation ID: <uuid>       │
          │     └─ request_method: POST          │
          │                                      │
          │  2. Route Handler: create_request    │
          │     ├─ Validate schema (Pydantic)    │
          │     ├─ Check duplicates (Query DB)   │
          │     ├─ Call service layer            │
          │     └─ Return 201 Created            │
          │                                      │
          │  3. Service: create_request          │
          │     ├─ Generate request_number       │
          │     ├─ Create ORM object             │
          │     ├─ db.add() + db.flush()         │
          │     ├─ db.commit()                   │
          │     └─ db.refresh()                  │
          │                                      │
          │  4. Middleware: Log response         │
          │     ├─ Log: request_completed        │
          │     ├─ status_code: 201              │
          │     └─ duration_ms: 45               │
          │                                      │
          └──────────────────────────────────────┘
                                 ↓
          ┌──────────────────────────────────────┐
          │   Database Transaction                │
          │                                      │
          │  1. Query: Check duplicate           │
          │     SELECT * FROM institutional_     │
          │     requests WHERE                   │
          │     external_id = 'EXT-001'          │
          │     → Not found ✓                    │
          │                                      │
          │  2. Insert new request                │
          │     INSERT INTO institutional_       │
          │     requests (external_id, ...)      │
          │     VALUES ('EXT-001', ...)          │
          │     → ID: 1 ✓                        │
          │                                      │
          │  3. Commit transaction               │
          │     COMMIT                           │
          │                                      │
          └──────────────────────────────────────┘
                                 ↓
          ┌──────────────────────────────────────┐
          │   Sidecar: Send logs to CloudWatch   │
          │                                      │
          │  Logs stream:                        │
          │  /ecs/esic-backend/                  │
          │  backend/prod-task-<id>              │
          │                                      │
          │  Each log entry (JSON):              │
          │  {                                   │
          │    "timestamp": "2024-01-15T...",   │
          │    "level": "INFO",                  │
          │    "logger": "app.api.routes",       │
          │    "message": "create_request_...",  │
          │    "correlation_id": "req-001"       │
          │  }                                   │
          │                                      │
          └──────────────────────────────────────┘
                                 ↓
          ┌──────────────────────────────────────┐
          │   Return response to ALB             │
          │                                      │
          │  HTTP 201 Created                    │
          │  Headers:                            │
          │  - Content-Type: application/json    │
          │  - X-Correlation-ID: req-001         │
          │  - Server: FastAPI                   │
          │                                      │
          │  Body:                               │
          │  {                                   │
          │    "id": 1,                          │
          │    "request_number": "SOL-ABC1",     │
          │    "external_id": "EXT-001",         │
          │    "status": "recibida",             │
          │    ...                               │
          │  }                                   │
          │                                      │
          └──────────────────────────────────────┘
                                 ↓
          ┌──────────────────────────────────────┐
          │   ALB sends response to client       │
          │                                      │
          │  TLS encrypt + send                  │
          │  Total latency: ~100ms               │
          │  (50ms app + 50ms network)           │
          │                                      │
          └──────────────────────────────────────┘
                                 ↓
          ┌──────────────────────────────────────┐
          │   CloudWatch metrics recorded        │
          │                                      │
          │  Metrics:                            │
          │  - RequestCount++                    │
          │  - StatusCode201++                   │
          │  - ResponseTime: 100ms               │
          │  - TargetHealth: Healthy             │
          │                                      │
          │  Logs indexed & queryable:           │
          │  - By correlation_id                 │
          │  - By status_code                    │
          │  - By duration_ms                    │
          │                                      │
          └──────────────────────────────────────┘
```

---

## Error Handling Flow

```
┌────────────────────────────────────────────────────────────┐
│         USER REQUEST: POST /solicitudes/                   │
│         Body: { external_id: "EXT-001" } ← DUPLICATE       │
└────────────────────────────────────────────────────────────┘
                         ↓
            [Proceed through ALB routing]
                         ↓
        ┌──────────────────────────────────┐
        │  ECS Task receives request        │
        │                                  │
        │  Service Layer:                  │
        │  1. Query DB for duplicate       │
        │  2. Result: FOUND (ID=5)         │
        │  3. Raise DuplicateExternal     │
        │     IdError                      │
        │                                  │
        └──────────────────────────────────┘
                         ↓
        ┌──────────────────────────────────┐
        │  Route Handler catches exception │
        │                                  │
        │  except DuplicateExternalIdError │
        │  as e:                           │
        │    return HTTPException(         │
        │      status_code=409,            │
        │      detail=str(e)               │
        │    )                             │
        │                                  │
        └──────────────────────────────────┘
                         ↓
        ┌──────────────────────────────────┐
        │  Log warning                     │
        │                                  │
        │  "create_request_duplicate"      │
        │  {                               │
        │    "external_id": "EXT-001",     │
        │    "existing_id": 5,             │
        │    "status_code": 409            │
        │  }                               │
        │                                  │
        └──────────────────────────────────┘
                         ↓
        ┌──────────────────────────────────┐
        │  Return 409 Conflict response    │
        │                                  │
        │  HTTP 409 Conflict               │
        │  Content-Type: application/json  │
        │  X-Correlation-ID: req-002       │
        │                                  │
        │  {                               │
        │    "detail": "Solicitud con ...  │
        │     (ID: 5)"                     │
        │  }                               │
        │                                  │
        └──────────────────────────────────┘
                         ↓
        ┌──────────────────────────────────┐
        │  CloudWatch metrics              │
        │                                  │
        │  - RequestCount++                │
        │  - StatusCode409++               │
        │  - DuplicateDetected++           │
        │                                  │
        │  Alert (if spike):               │
        │  "DuplicateExternalIdSpike" →   │
        │  SNS → Email/PagerDuty          │
        │                                  │
        └──────────────────────────────────┘
```

---

## Consumer Service Flow (Scheduled)

```
┌─────────────────────────────────────────────────────────────┐
│              CloudWatch Events Rule                         │
│              Trigger: Cron 0 */6 * * ? (Every 6 hours)     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│           ECS Scheduled Task Launches                       │
│                                                             │
│  Task Definition: esic-consumer-task                       │
│  - CPU: 256 (0.25 vCPU)                                    │
│  - Memory: 512 MB                                          │
│  - Container: esic-consumer:latest                         │
│  - Timeout: 600 segundos                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│        Consumer Application Starts                          │
│                                                             │
│  1. Initialize RequestConsumer                             │
│     - base_url: http://esic-backend-alb:8000              │
│     - max_retries: 3                                       │
│     - timeout: 30 segundos                                 │
│                                                             │
│  2. Health Check                                           │
│     GET /health → 200 OK ✓                                 │
│                                                             │
│  3. Readiness Check                                        │
│     GET /health/ready → database: connected ✓             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
        ┌──────────────────────────────────┐
        │  Create 5 test requests           │
        │                                  │
        │  Loop through requests:          │
        │    POST /solicitudes/             │
        │    - external_id: EXT-<N>        │
        │    - requester_name: User <N>    │
        │    - ...                         │
        │    - Max 3 retries on 5xx        │
        │    - No retry on 4xx              │
        │                                  │
        └──────────────────────────────────┘
                         ↓
    ┌──────────────────────────────────────────┐
    │  Log Results to CloudWatch               │
    │                                          │
    │  {                                       │
    │    "message": "execution_summary",       │
    │    "correlation_id": "<uuid>",           │
    │    "total_attempts": 5,                  │
    │    "successful": 5,                      │
    │    "failed": 0,                          │
    │    "conflicts": 0,                       │
    │    "duration_ms": 2500                   │
    │  }                                       │
    │                                          │
    └──────────────────────────────────────────┘
                         ↓
    ┌──────────────────────────────────────────┐
    │  ECS Task completes                      │
    │                                          │
    │  Exit code: 0 (success)                  │
    │  Logs available in CloudWatch             │
    │  /ecs/esic-backend/consumer/<task-id>    │
    │                                          │
    └──────────────────────────────────────────┘
```

---

## Auto-Scaling Scenario

```
Normal State (2 tasks):
├─ Task 1: CPU 40%, Memory 60% ✓ Healthy
└─ Task 2: CPU 45%, Memory 65% ✓ Healthy

            ↓ (Sudden spike: 100 concurrent users)

Alarm State:
├─ Task 1: CPU 92% ⚠ High
├─ Task 2: CPU 88% ⚠ High
└─ Average CPU: 90% > Target (70%)

            ↓ (Auto Scaling detects)

Scale-Out Decision:
├─ CloudWatch metric: Average CPU > 70%
├─ Cooldown: 300 segundos
├─ Decision: Add 2 tasks (reaching Max before 200%)
└─ Target: 4 tasks total

            ↓ (ECS launches new tasks)

During Scale-Out:
├─ Task 1: Running (existing)
├─ Task 2: Running (existing)
├─ Task 3: Provisioning (new)
└─ Task 4: Provisioning (new)

            ↓ (Tasks become healthy in ~60 segundos)

New Healthy State (4 tasks):
├─ Task 1: CPU 50%, Memory 55%
├─ Task 2: CPU 52%, Memory 56%
├─ Task 3: CPU 48%, Memory 53%
└─ Task 4: CPU 49%, Memory 54%

            ↓ (Spike passes, CPU back to normal)

Scale-In Decision:
├─ Average CPU: 50% < 30% (scale-in threshold)
├─ Cooldown: 300 segundos
├─ Wait: 5 minutes before scale-in
└─ After 5min cooldown: Reduce 1 task

Final State (3 tasks, or back to 2):
└─ Gradual scale-down to configured minimum
```

---

## Disaster Recovery Flow

```
Normal Operations:
├─ Primary RDS: AZ-1a (us-east-1a) ✓ Healthy
├─ Standby RDS: AZ-1b (us-east-1b) ✓ Synchronized
├─ ECS Tasks: Distributed across both AZs
└─ ALB: Health checks passing

            ↓ (Primary AZ-1a fails)

Failure Detection:
├─ RDS primary instance becomes unavailable
├─ ECS tasks in AZ-1a become unhealthy
├─ ALB health checks start failing
└─ CloudWatch detects ~3 sequential failures

            ↓ (RDS Multi-AZ Failover - Automatic < 2 min)

Failover Process:
├─ Promote Standby to Primary (AZ-1b)
├─ DNS endpoint remains same (internal)
├─ New standby spins up in AZ-1a
└─ Application reconnects automatically

            ↓ (ECS Auto Recovery)

Recovery:
├─ Unhealthy ECS tasks are deregistered
├─ Healthy tasks in AZ-1b continue serving
├─ Auto Scaling launches new tasks in AZ-1c (if available)
└─ ALB redistributes traffic

            ↓ (AZ-1a recovers)

Full Recovery:
├─ New infrastructure spins up in AZ-1a
├─ ECS tasks become healthy
├─ Requests flow to both AZs again
├─ RDS creates new standby in AZ-1a
└─ System back to normal ✓

Recovery Metrics:
├─ Detection time: ~30 segundos
├─ RDS Failover: < 2 minutos
├─ Application recovery: ~3 minutos
├─ Full system: ~5 minutos
└─ Data loss: 0 (RDS Multi-AZ sync)
```

---

## Monitoring & Alerting Chain

```
Application Issue
       ↓
     ↙ ↓ ↖
    /  |  \

[Logs]    [Metrics]    [Health Checks]
   ↓         ↓              ↓
   │         │              │
   └─→ CloudWatch ←─────────┘
        (Aggregation)
        
        Queries:
        - Errors per minute
        - Request latency
        - Task health
        - Database connections
        
            ↓
        
      [CloudWatch Alarms]
      
      alarm_1: error_rate > 5%
      alarm_2: response_time > 1s
      alarm_3: unhealthy_targets > 0
      
            ↓
        
      [SNS Topic: esic-alerts]
      
      Email: ops@example.com
      PagerDuty: esic-team
      Lambda: auto-remediation
      
            ↓
        
    [Human Response]
    ├─ Check logs in CloudWatch Insights
    ├─ Review X-Ray traces
    ├─ Manual scale-up if needed
    └─ Prepare incident report
```

---

## Summary

Esta arquitectura proporciona un flujo de solicitudes completamente observable,
escalable automáticamente y resiliente a fallos de componentes individuales.
Cada punto de estrés tiene logging, métricas y alertas asociadas.
