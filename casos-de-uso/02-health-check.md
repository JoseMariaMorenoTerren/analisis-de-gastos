# Caso de Uso 02: Health Check (Verificación de Salud)

## Descripción
Este caso de uso describe el endpoint de verificación de salud (health check) para todos los microservicios de la aplicación. Los health checks permiten monitorear el estado de cada servicio y sus dependencias, facilitando el diagnóstico de problemas y la implementación de balanceadores de carga, orquestadores de contenedores y sistemas de monitoreo.

## Actores
- Sistema de Monitoreo (Prometheus, Grafana, etc.)
- Balanceador de Carga (Load Balancer)
- Orquestador de Contenedores (Kubernetes, Docker Swarm)
- Equipo de Operaciones (DevOps)
- Equipo de Desarrollo

## Precondiciones
- El microservicio debe estar en ejecución
- El endpoint de health check debe estar disponible sin requerir autenticación

## Microservicios Aplicables

Este caso de uso se aplica a los tres microservicios:

1. **Microservicio de Autenticación** (Puerto 8001)
   - Endpoint: `GET /api/v1/health`
   - Dependencias: Base de datos de usuarios

2. **Microservicio de Recopilación de Datos** (Puerto 8002)
   - Endpoint: `GET /api/v1/health`
   - Dependencias: Base de datos de gastos, Servicio de Autenticación

3. **Microservicio de Manipulación de Datos** (Puerto 8003)
   - Endpoint: `GET /api/v1/health`
   - Dependencias: Base de datos de análisis, Servicio de Recopilación

## Flujo Principal

### 1. Solicitud de Health Check
El cliente (sistema de monitoreo) envía una petición GET al endpoint de health.

**Endpoint:** `GET /api/v1/health`

**Headers:** Ninguno requerido (endpoint público)

### 2. Verificación del Estado
El microservicio:
- Verifica su propio estado interno
- Comprueba la conectividad con sus dependencias (base de datos, otros servicios)
- Calcula métricas de salud (tiempo de actividad, uso de recursos si aplica)

### 3. Respuesta Exitosa (Servicio Saludable)
El sistema devuelve información del estado del servicio.

**Código HTTP:** `200 OK`

**Estructura de la respuesta:**
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0",
  "timestamp": "2025-12-30T10:30:00Z",
  "uptime": 86400,
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 15
    }
  }
}
```

## Flujos Alternativos

### A1: Servicio Degradado (Dependencia con Problemas)
**Condición:** El servicio está funcionando pero una dependencia no crítica tiene problemas

**Código HTTP:** `200 OK`

**Respuesta:**
```json
{
  "status": "degraded",
  "service": "data-collection-service",
  "version": "1.0.0",
  "timestamp": "2025-12-30T10:30:00Z",
  "uptime": 86400,
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 12
    },
    "auth_service": {
      "status": "unhealthy",
      "response_time_ms": 5000,
      "error": "Connection timeout"
    }
  }
}
```

### A2: Servicio No Saludable (Fallo Crítico)
**Condición:** El servicio tiene un problema crítico que impide su funcionamiento normal

**Código HTTP:** `503 Service Unavailable`

**Respuesta:**
```json
{
  "status": "unhealthy",
  "service": "auth-service",
  "version": "1.0.0",
  "timestamp": "2025-12-30T10:30:00Z",
  "uptime": 86400,
  "checks": {
    "database": {
      "status": "unhealthy",
      "response_time_ms": null,
      "error": "Connection refused"
    }
  }
}
```

### A3: Servicio Iniciándose (Starting)
**Condición:** El servicio está en proceso de inicialización

**Código HTTP:** `503 Service Unavailable`

**Respuesta:**
```json
{
  "status": "starting",
  "service": "data-manipulation-service",
  "version": "1.0.0",
  "timestamp": "2025-12-30T10:30:00Z",
  "uptime": 5,
  "checks": {
    "database": {
      "status": "connecting",
      "response_time_ms": null
    }
  }
}
```

## Poscondiciones
- **Éxito:** El cliente recibe información precisa sobre el estado del servicio
- **Fallo:** El cliente puede detectar problemas y tomar acciones correctivas

## Requisitos No Funcionales

### Rendimiento
- El endpoint debe responder en menos de 100ms en condiciones normales
- No debe consumir recursos significativos del sistema
- Debe ser ligero y eficiente

### Disponibilidad
- El endpoint debe estar disponible incluso cuando otras partes del servicio fallen
- Debe ser el primer endpoint en estar disponible al iniciar el servicio
- Debe ser el último en dejar de responder al detener el servicio

### Seguridad
- No requiere autenticación (endpoint público)
- No debe exponer información sensible (credenciales, configuraciones)
- Puede incluir información básica de versión y estado

## Detalles de Implementación

### Estados Posibles

| Estado | Código HTTP | Descripción |
|--------|-------------|-------------|
| `healthy` | 200 OK | Servicio funcionando correctamente |
| `degraded` | 200 OK | Servicio funcionando con limitaciones |
| `unhealthy` | 503 Service Unavailable | Servicio con fallos críticos |
| `starting` | 503 Service Unavailable | Servicio iniciándose |

### Checks por Microservicio

#### Microservicio de Autenticación
- `database`: Conexión a la base de datos de usuarios
- `redis` (futuro): Cache de sesiones

#### Microservicio de Recopilación de Datos
- `database`: Conexión a la base de datos de gastos
- `auth_service`: Conectividad con el servicio de autenticación
- `storage` (futuro): Sistema de almacenamiento de archivos

#### Microservicio de Manipulación de Datos
- `database`: Conexión a la base de datos de análisis
- `data_collection_service`: Conectividad con el servicio de recopilación
- `cache` (futuro): Sistema de caché para análisis

### Campos de la Respuesta

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `status` | string | Sí | Estado general del servicio |
| `service` | string | Sí | Nombre del microservicio |
| `version` | string | Sí | Versión del servicio |
| `timestamp` | string (ISO 8601) | Sí | Marca de tiempo de la verificación |
| `uptime` | integer | Sí | Tiempo en segundos desde que el servicio inició |
| `checks` | object | Sí | Mapa de verificaciones de dependencias |

### Formato del Objeto Check

```json
{
  "nombre_dependencia": {
    "status": "healthy|degraded|unhealthy|connecting",
    "response_time_ms": 15,
    "error": "Mensaje de error opcional"
  }
}
```

## Casos de Uso en Sistemas de Monitoreo

### Kubernetes Liveness Probe
```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8001
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Kubernetes Readiness Probe
```yaml
readinessProbe:
  httpGet:
    path: /api/v1/health
    port: 8001
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3
```

### Docker Healthcheck
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/api/v1/health || exit 1
```

### Prometheus Monitoring
```yaml
- job_name: 'auth-service'
  metrics_path: '/api/v1/health'
  static_configs:
    - targets: ['localhost:8001']
```

## Diagrama de Flujo

```
┌─────────────────┐              ┌──────────────────┐
│ Sistema de      │              │ Microservicio    │
│ Monitoreo       │              │                  │
└────────┬────────┘              └────────┬─────────┘
         │                                │
         │ GET /api/v1/health             │
         ├───────────────────────────────>│
         │                                │
         │                                ├─ Verificar estado interno
         │                                │
         │                                ├─ Verificar base de datos
         │                                │
         │                                ├─ Verificar dependencias
         │                                │
         │                                ├─ Calcular métricas
         │                                │
         │ 200 OK / 503 Unavailable       │
         │ {status, service, checks...}   │
         │<───────────────────────────────┤
         │                                │
         ├─ Registrar métricas            │
         │                                │
         ├─ Alertar si unhealthy          │
         │                                │
```

## Beneficios

1. **Detección Temprana de Problemas**: Identificar fallos antes de que afecten a los usuarios
2. **Automatización**: Permite reinicio automático de servicios problemáticos
3. **Monitoreo Continuo**: Visibilidad del estado de todos los servicios 24/7
4. **Balanceo de Carga**: Los balanceadores pueden redirigir tráfico de servicios no saludables
5. **Troubleshooting**: Facilita la identificación rápida de la causa raíz de problemas

## Notas Adicionales

- Los health checks NO deben requerir autenticación
- Deben ser rápidos y ligeros (< 100ms)
- No deben realizar operaciones costosas
- Deben cachear resultados de checks pesados si es necesario
- La frecuencia de verificación debe ser configurable
- Los timeouts deben ser apropiados para cada dependencia
