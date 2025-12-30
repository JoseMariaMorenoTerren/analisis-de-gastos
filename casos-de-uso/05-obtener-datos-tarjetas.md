# Caso de Uso 05: Obtener Datos de Tarjetas

## Descripción
Este endpoint permite obtener todos los registros de las tarjetas de crédito/débito que han sido cargados desde los archivos CSV en el entorno especificado. Los datos se devuelven concatenados de todos los archivos cargados y con soporte de paginación.

## Endpoint
- **URL**: `/api/v1/data/cards`
- **Método**: `GET`
- **Puerto**: 8002 (Servicio de Recopilación de Datos)
- **Autenticación**: Requerida (Bearer Token)

## Parámetros de Query

| Parámetro | Tipo | Requerido | Valor por defecto | Descripción |
|-----------|------|-----------|-------------------|-------------|
| `environment` | string | Sí | - | Entorno de datos: `pre` o `pro` |
| `page` | integer | No | 1 | Número de página a obtener (base 1) |
| `page_size` | integer | No | 2000 | Cantidad de registros por página (máximo 2000) |

## Request

### Headers
```http
GET /api/v1/data/cards?environment=pre&page=1&page_size=2000 HTTP/1.1
Host: localhost:8002
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Ejemplos de Query Strings

**Obtener primera página con tamaño por defecto (2000 registros):**
```
GET /api/v1/data/cards?environment=pre
```

**Obtener segunda página con 100 registros por página:**
```
GET /api/v1/data/cards?environment=pre&page=2&page_size=100
```

**Obtener datos de producción:**
```
GET /api/v1/data/cards?environment=pro&page=1&page_size=2000
```

## Response

### Caso Exitoso (200 OK)

```json
{
  "success": true,
  "message": "Datos de tarjetas obtenidos exitosamente",
  "data": {
    "environment": "pre",
    "pagination": {
      "current_page": 1,
      "page_size": 2000,
      "total_records": 230,
      "total_pages": 1,
      "has_next": false,
      "has_previous": false
    },
    "records": [
      {
        "operacion": "C",
        "fecha_hora": "2024-10-16 10:30:00",
        "tipo": "COMPRA EN ESTABLECIMIENTO",
        "importe": -45.80,
        "comision": 0.0,
        "establecimiento": "SUPERMERCADO XYZ",
        "source_file": "MOV22698582-110225104150.csv"
      },
      {
        "operacion": "C",
        "fecha_hora": "2024-10-17 15:22:00",
        "tipo": "COMPRA ONLINE",
        "importe": -89.99,
        "comision": 0.0,
        "establecimiento": "TIENDA ONLINE ABC",
        "source_file": "MOV22698582-110225104150.csv"
      }
      // ... más registros hasta completar la página
    ],
    "retrieved_at": "2025-12-30T14:30:00Z"
  }
}
```

### Caso: Entorno sin datos (200 OK)

Cuando el entorno especificado no tiene archivos cargados:

```json
{
  "success": true,
  "message": "No hay datos disponibles en el entorno especificado",
  "data": {
    "environment": "pro",
    "pagination": {
      "current_page": 1,
      "page_size": 2000,
      "total_records": 0,
      "total_pages": 0,
      "has_next": false,
      "has_previous": false
    },
    "records": [],
    "retrieved_at": "2025-12-30T14:30:00Z"
  }
}
```

### Caso: Página fuera de rango (400 Bad Request)

Cuando se solicita una página que no existe:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PAGE",
    "message": "La página solicitada no existe. Total de páginas: 1"
  }
}
```

### Caso: Parámetro page_size inválido (400 Bad Request)

Cuando el tamaño de página excede el máximo o es inválido:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PAGE_SIZE",
    "message": "El tamaño de página debe estar entre 1 y 2000"
  }
}
```

### Caso: Parámetro environment faltante (400 Bad Request)

```json
{
  "success": false,
  "error": {
    "code": "MISSING_PARAMETER",
    "message": "El parámetro 'environment' es requerido"
  }
}
```

### Caso: Environment inválido (400 Bad Request)

```json
{
  "success": false,
  "error": {
    "code": "INVALID_ENVIRONMENT",
    "message": "El entorno debe ser 'pre' o 'pro'"
  }
}
```

### Caso: Token de autenticación inválido (401 Unauthorized)

```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Token de autenticación inválido o expirado"
  }
}
```

### Caso: Sin token de autenticación (401 Unauthorized)

```json
{
  "success": false,
  "error": {
    "code": "MISSING_TOKEN",
    "message": "Token de autenticación no proporcionado"
  }
}
```

## Estructura de Datos

### Objeto Record

Los registros devueltos en el array `records` tienen la siguiente estructura basada en las columnas de los archivos CSV:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `operacion` | string | Tipo de operación (C=Cargo, A=Abono, etc.) |
| `fecha_hora` | string (datetime) | Fecha y hora de la operación (YYYY-MM-DD HH:MM:SS) |
| `tipo` | string | Tipo/descripción de la operación |
| `importe` | number | Importe de la operación (puede ser negativo) |
| `comision` | number | Comisión aplicada a la operación |
| `establecimiento` | string | Nombre del establecimiento |
| `source_file` | string | Nombre del archivo CSV de origen |

### Objeto Pagination

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `current_page` | integer | Página actual (base 1) |
| `page_size` | integer | Cantidad de registros por página |
| `total_records` | integer | Total de registros disponibles |
| `total_pages` | integer | Total de páginas disponibles |
| `has_next` | boolean | Indica si hay una página siguiente |
| `has_previous` | boolean | Indica si hay una página anterior |

## Reglas de Negocio

1. **Concatenación de archivos**: 
   - Se deben concatenar todos los archivos CSV del entorno especificado
   - Se excluyen archivos Excel (estos se obtienen con el endpoint de cuenta)
   - Los registros se ordenan por fecha y hora (campo `fecha_hora`) de forma ascendente

2. **Paginación**:
   - El tamaño de página por defecto es 2000 registros
   - El tamaño máximo de página es 2000 registros
   - La primera página es la número 1 (no 0)
   - Si se solicita una página mayor al total de páginas, se devuelve error 400

3. **Formato de fechas**:
   - Las fechas se devuelven en formato ISO (YYYY-MM-DD HH:MM:SS)
   - Si las fechas en el archivo están en otro formato (DD/MM/YYYY), se convierten

4. **Source file**:
   - Cada registro incluye el campo `source_file` con el nombre del archivo de origen
   - Esto permite rastrear de qué archivo proviene cada registro

5. **Autenticación**:
   - El endpoint requiere autenticación mediante Bearer Token
   - El token debe ser válido y no estar expirado

## Casos de Prueba

### Pruebas de Integración

1. ✅ **test_get_card_data_requires_authentication**
   - Verificar que sin token devuelve 401

2. ✅ **test_get_card_data_requires_environment_parameter**
   - Verificar que sin parámetro environment devuelve 400

3. ✅ **test_get_card_data_invalid_environment**
   - Verificar que environment='invalid' devuelve 400

4. ✅ **test_get_card_data_pre_success**
   - Verificar que con environment=pre devuelve 200
   - Verificar estructura de respuesta correcta

5. ✅ **test_get_card_data_pre_has_correct_record_count**
   - Para entorno PRE con 1 archivo CSV (230 registros)
   - Verificar que total_records = 230

6. ✅ **test_get_card_data_pre_pagination_metadata**
   - Verificar que con page_size=2000 y 230 registros:
     - total_pages = 1
     - has_next = false
     - has_previous = false

7. ✅ **test_get_card_data_record_structure**
   - Verificar que cada record tiene: operacion, fecha_hora, tipo, importe, comision, establecimiento, source_file
   - Verificar que las fechas están en formato YYYY-MM-DD HH:MM:SS

8. ✅ **test_get_card_data_includes_source_file**
   - Verificar que todos los registros tienen el campo source_file
   - Verificar que el source_file corresponde a archivos CSV

9. ✅ **test_get_card_data_small_page_size**
   - Solicitar page_size=10 con 230 registros
   - Verificar que total_pages = 23 (ceil(230/10))
   - Verificar que devuelve exactamente 10 registros en página 1

10. ✅ **test_get_card_data_last_page**
    - Solicitar última página con page_size=10
    - Verificar que devuelve 10 registros (230 % 10 = 0, pero 230/10 = 23)
    - Verificar has_next = false

11. ✅ **test_get_card_data_page_out_of_range**
    - Solicitar página 999
    - Verificar que devuelve 400

12. ✅ **test_get_card_data_invalid_page_size**
    - Solicitar page_size=3000 (mayor al máximo)
    - Verificar que devuelve 400

13. ✅ **test_get_card_data_records_ordered_by_datetime**
    - Verificar que los registros están ordenados por fecha_hora ascendente

14. ✅ **test_get_card_data_pro_empty**
    - Solicitar datos de entorno PRO (sin datos)
    - Verificar que devuelve 200 con records=[]

## Dependencias

- **Caso de Uso 03**: Los datos deben haberse cargado previamente mediante el endpoint de carga de datos
- **Caso de Uso 01**: Requiere autenticación válida

## Notas Técnicas

- Los datos se obtienen de archivos CSV previamente cargados en memoria o base de datos
- Los archivos Excel se excluyen de este endpoint (tienen su propio endpoint - caso 04)
- La implementación debe ser eficiente para manejar grandes volúmenes de datos
- Considerar caché para mejorar rendimiento en consultas repetidas
- Los archivos CSV usan delimitador punto y coma (;) y codificación latin1
