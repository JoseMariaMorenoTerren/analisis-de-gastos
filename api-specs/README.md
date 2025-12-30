# Especificaciones OpenAPI

Este directorio contiene las especificaciones OpenAPI 3.0 para todos los microservicios de la aplicación de análisis de gastos.

## 📁 Estructura

```
api-specs/
├── auth-service-openapi.yaml              # Microservicio de Autenticación
├── data-collection-service-openapi.yaml   # Microservicio de Recopilación (pendiente)
├── data-manipulation-service-openapi.yaml # Microservicio de Manipulación (pendiente)
└── README.md                              # Este archivo
```

## 🔧 Microservicios Documentados

### ✅ Microservicio de Autenticación (Puerto 8001)
**Archivo:** `auth-service-openapi.yaml`

**Endpoints implementados:**
- `POST /api/v1/auth/login` - Autenticación de usuarios

**Endpoints futuros:**
- `POST /api/v1/auth/logout` - Cerrar sesión
- `POST /api/v1/auth/refresh` - Renovar token

### ⏳ Microservicio de Recopilación de Datos (Puerto 8002)
**Archivo:** `data-collection-service-openapi.yaml` (pendiente)

**Endpoints planificados:**
- Registro de gastos
- Listado de gastos
- Actualización de gastos
- Eliminación de gastos

### ⏳ Microservicio de Manipulación de Datos (Puerto 8003)
**Archivo:** `data-manipulation-service-openapi.yaml` (pendiente)

**Endpoints planificados:**
- Análisis de gastos por categoría
- Estadísticas y reportes
- Predicciones y tendencias

## 📖 Visualización de las Especificaciones

### Opción 1: Swagger Editor Online
1. Visita [editor.swagger.io](https://editor.swagger.io/)
2. Copia y pega el contenido del archivo YAML
3. La documentación interactiva se generará automáticamente

### Opción 2: Swagger UI Local
Instalar y ejecutar Swagger UI localmente:

```bash
# Usando Docker
docker run -p 80:8080 -e SWAGGER_JSON=/specs/auth-service-openapi.yaml \
  -v $(pwd)/api-specs:/specs swaggerapi/swagger-ui

# Acceder en: http://localhost
```

### Opción 3: VS Code Extension
Instala la extensión "OpenAPI (Swagger) Editor" en VS Code:
1. Abre VS Code
2. Ve a Extensions (Cmd+Shift+X)
3. Busca "OpenAPI (Swagger) Editor"
4. Instala y abre cualquier archivo `.yaml`

### Opción 4: Redoc
Para una documentación más elegante:

```bash
# Usando npx
npx @redocly/cli preview-docs api-specs/auth-service-openapi.yaml

# O con Docker
docker run -p 8080:80 \
  -v $(pwd)/api-specs:/usr/share/nginx/html/specs \
  -e SPEC_URL=specs/auth-service-openapi.yaml \
  redocly/redoc
```

## 🔍 Validación de Especificaciones

### Validar sintaxis YAML
```bash
# Usando yamllint
pip install yamllint
yamllint api-specs/auth-service-openapi.yaml

# O usando yq
brew install yq
yq eval api-specs/auth-service-openapi.yaml
```

### Validar especificación OpenAPI
```bash
# Usando swagger-cli
npm install -g @apidevtools/swagger-cli
swagger-cli validate api-specs/auth-service-openapi.yaml

# Usando openapi-generator
brew install openapi-generator
openapi-generator validate -i api-specs/auth-service-openapi.yaml
```

## 🚀 Generación de Código

### Generar cliente en Python
```bash
openapi-generator generate \
  -i api-specs/auth-service-openapi.yaml \
  -g python \
  -o clients/python-auth-client
```

### Generar cliente en JavaScript/TypeScript
```bash
openapi-generator generate \
  -i api-specs/auth-service-openapi.yaml \
  -g typescript-axios \
  -o clients/typescript-auth-client
```

### Generar servidor Flask (Python)
```bash
openapi-generator generate \
  -i api-specs/auth-service-openapi.yaml \
  -g python-flask \
  -o services/auth-service-generated
```

## 📝 Convenciones

### Nomenclatura de Endpoints
- Usar kebab-case para URLs: `/api/v1/auth/login`
- Versionar la API: `/api/v1/...`
- Usar sustantivos en plural para colecciones: `/api/v1/users`
- Usar verbos HTTP apropiados: GET, POST, PUT, PATCH, DELETE

### Códigos de Estado HTTP
- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Error en la solicitud (validación)
- **401 Unauthorized**: Autenticación requerida o fallida
- **403 Forbidden**: Sin permisos para acceder al recurso
- **404 Not Found**: Recurso no encontrado
- **429 Too Many Requests**: Rate limit excedido
- **500 Internal Server Error**: Error del servidor
- **503 Service Unavailable**: Servicio temporalmente no disponible

### Estructura de Respuestas
Todas las respuestas JSON siguen esta estructura:

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Mensaje descriptivo",
  "data": { /* datos relevantes */ }
}
```

**Respuesta de error:**
```json
{
  "success": false,
  "message": "Mensaje de error",
  "error_code": "CODIGO_ERROR"
}
```

**Respuesta de error de validación:**
```json
{
  "success": false,
  "message": "Mensaje general",
  "errors": {
    "campo1": ["Error 1", "Error 2"],
    "campo2": ["Error 1"]
  },
  "error_code": "VALIDATION_ERROR"
}
```

## 🔐 Seguridad

### Autenticación
Los endpoints protegidos requieren un token JWT en el header:
```
Authorization: Bearer <token>
```

### Rate Limiting
Todos los endpoints implementan rate limiting con headers informativos:
- `X-RateLimit-Limit`: Límite de peticiones
- `X-RateLimit-Remaining`: Peticiones restantes
- `X-RateLimit-Reset`: Timestamp de reinicio
- `Retry-After`: Segundos para reintentar (solo en 429)

## 📊 Versionado

Las especificaciones OpenAPI siguen versionado semántico:
- **Major**: Cambios incompatibles con versiones anteriores
- **Minor**: Nueva funcionalidad compatible hacia atrás
- **Patch**: Correcciones de bugs

## 🔄 Actualización

Cuando se actualice una especificación:
1. Actualizar el número de versión en `info.version`
2. Documentar cambios en un changelog
3. Validar la especificación
4. Actualizar los tests de integración correspondientes
5. Regenerar clientes si es necesario

## 📚 Referencias

- [OpenAPI Specification](https://swagger.io/specification/)
- [OpenAPI Best Practices](https://swagger.io/resources/articles/best-practices-in-api-design/)
- [Swagger Editor](https://editor.swagger.io/)
- [OpenAPI Generator](https://openapi-generator.tech/)
