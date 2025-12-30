# Caso de Uso 03: Carga de Datos desde Archivos

## Descripción
Este caso de uso describe el proceso de carga de datos de gastos desde archivos CSV o Excel (XLS/XLSX) almacenados en carpetas del sistema. El microservicio de recopilación de datos permite cargar archivos desde dos entornos diferentes: PRE (datos de prueba) y PRO (datos de producción).

## Actores
- Usuario autenticado (mediante token JWT)
- Microservicio de Recopilación de Datos

## Precondiciones
- El usuario debe estar autenticado (token JWT válido)
- Los archivos deben existir en la carpeta correspondiente (datos-pre o datos-pro)
- Los archivos deben tener formato CSV o Excel (XLS/XLSX)
- Los archivos deben contener una columna de fecha
- El microservicio de recopilación de datos debe estar operativo

## Tipos de Carga

### 1. Carga desde PRE (Datos de Prueba)
- **Carpeta:** `datos-pre/`
- **Uso:** Desarrollo, testing, pruebas
- **Endpoint:** `POST /api/v1/data/load/pre`

### 2. Carga desde PRO (Datos de Producción)
- **Carpeta:** `datos-pro/`
- **Uso:** Producción, datos reales
- **Endpoint:** `POST /api/v1/data/load/pro`

## Flujo Principal - Carga desde PRE

### 1. Solicitud de Carga
El cliente envía una petición POST al endpoint de carga PRE.

**Endpoint:** `POST /api/v1/data/load/pre`

**Headers requeridos:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body (opcional):**
```json
{
  "clear_existing": false
}
```

### 2. Validación de Autenticación
El microservicio:
- Valida el token JWT con el servicio de autenticación
- Verifica que el usuario tenga permisos para cargar datos

### 3. Lectura de Archivos
El microservicio:
- Accede a la carpeta `datos-pre/`
- Identifica todos los archivos CSV, XLS y XLSX
- Lee cada archivo y lo carga en memoria

### 4. Procesamiento de Datos
Para cada archivo, el microservicio:
- Cuenta el número de registros (filas)
- Identifica la columna de fecha
- Extrae la fecha mínima (fecha_inicio)
- Extrae la fecha máxima (fecha_fin)
- Valida que el formato sea correcto

### 5. Almacenamiento en Memoria/Base de Datos
El microservicio:
- Almacena los datos en memoria o base de datos
- Mantiene metadatos de cada archivo cargado

### 6. Respuesta Exitosa
El sistema devuelve información detallada de la carga.

**Código HTTP:** `200 OK`

**Estructura de la respuesta:**
```json
{
  "success": true,
  "message": "Datos cargados exitosamente desde PRE",
  "data": {
    "environment": "pre",
    "total_files": 2,
    "total_records": 150,
    "files": [
      {
        "filename": "gastos_enero.csv",
        "format": "csv",
        "records": 85,
        "fecha_inicio": "2025-01-01",
        "fecha_fin": "2025-01-31",
        "size_bytes": 12456
      },
      {
        "filename": "gastos_febrero.xlsx",
        "format": "xlsx",
        "records": 65,
        "fecha_inicio": "2025-02-01",
        "fecha_fin": "2025-02-28",
        "size_bytes": 8932
      }
    ],
    "loaded_at": "2025-12-30T10:30:00Z"
  }
}
```

## Flujos Alternativos

### A1: No Hay Archivos en la Carpeta
**Condición:** La carpeta está vacía o no contiene archivos válidos

**Código HTTP:** `404 Not Found`

**Respuesta:**
```json
{
  "success": false,
  "message": "No se encontraron archivos para cargar en PRE",
  "error_code": "NO_FILES_FOUND"
}
```

### A2: Error al Leer Archivo
**Condición:** Un archivo no puede ser leído (corrupto, formato incorrecto)

**Código HTTP:** `422 Unprocessable Entity`

**Respuesta:**
```json
{
  "success": false,
  "message": "Error al procesar archivos",
  "errors": {
    "gastos_marzo.csv": [
      "Formato de archivo inválido",
      "No se encontró columna de fecha"
    ]
  },
  "error_code": "FILE_PROCESSING_ERROR",
  "data": {
    "processed_files": 1,
    "failed_files": 1
  }
}
```

### A3: Token No Válido o Expirado
**Condición:** El token JWT no es válido o ha expirado

**Código HTTP:** `401 Unauthorized`

**Respuesta:**
```json
{
  "success": false,
  "message": "Token inválido o expirado",
  "error_code": "INVALID_TOKEN"
}
```

### A4: Usuario Sin Permisos
**Condición:** El usuario no tiene permisos para cargar datos

**Código HTTP:** `403 Forbidden`

**Respuesta:**
```json
{
  "success": false,
  "message": "No tiene permisos para cargar datos",
  "error_code": "INSUFFICIENT_PERMISSIONS"
}
```

### A5: Archivo Demasiado Grande
**Condición:** Un archivo excede el tamaño máximo permitido (ej: 50MB)

**Código HTTP:** `413 Payload Too Large`

**Respuesta:**
```json
{
  "success": false,
  "message": "El archivo excede el tamaño máximo permitido",
  "errors": {
    "gastos_completo.xlsx": [
      "Tamaño: 75MB, Máximo permitido: 50MB"
    ]
  },
  "error_code": "FILE_TOO_LARGE"
}
```

## Poscondiciones
- **Éxito:** Los datos se cargan en memoria/base de datos y están disponibles para consulta
- **Fallo:** Se devuelve un mensaje de error descriptivo y los datos anteriores permanecen intactos

## Requisitos No Funcionales

### Rendimiento
- Debe procesar archivos de hasta 50MB
- Debe cargar al menos 10,000 registros por segundo
- El tiempo de respuesta debe ser proporcional al tamaño de los archivos

### Seguridad
- Solo usuarios autenticados pueden cargar datos
- Los archivos deben validarse para prevenir inyecciones
- No se debe exponer la estructura de carpetas del servidor

### Formatos Soportados
- **CSV:** Delimitador por coma, punto y coma, o tabulador
- **Excel:** XLS (Excel 97-2003), XLSX (Excel 2007+)
- **Codificación:** UTF-8, Latin-1

### Validaciones de Datos

#### Columnas Requeridas
Al menos una de estas columnas debe estar presente (detección automática):
- `fecha`, `date`, `Fecha`, `Date`, `FECHA`
- Formato aceptado: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, etc.

#### Columnas Opcionales Reconocidas
- `monto`, `amount`, `importe`, `valor`
- `descripcion`, `description`, `concepto`
- `categoria`, `category`, `tipo`

## Diferencias entre PRE y PRO

| Característica | PRE | PRO |
|----------------|-----|-----|
| Carpeta | `datos-pre/` | `datos-pro/` |
| Propósito | Testing, desarrollo | Producción |
| Validación | Menos estricta | Más estricta |
| Logs | Detallados | Resumidos |
| Backup automático | No | Sí |
| Límite de tamaño | 10MB | 50MB |

## Estructura de Archivos Esperada

### Ejemplo CSV (gastos_enero.csv)
```csv
fecha,descripcion,monto,categoria
2025-01-15,Supermercado,45.50,Alimentación
2025-01-16,Gasolina,60.00,Transporte
2025-01-17,Netflix,12.99,Entretenimiento
```

### Ejemplo Excel (gastos_febrero.xlsx)
```
| fecha      | descripcion  | monto | categoria       |
|------------|--------------|-------|-----------------|
| 2025-02-01 | Restaurante  | 35.00 | Alimentación    |
| 2025-02-05 | Metro        | 2.50  | Transporte      |
| 2025-02-10 | Cine         | 18.00 | Entretenimiento |
```

## Diagrama de Flujo

```
┌─────────┐                    ┌──────────────────┐
│ Cliente │                    │ Microservicio    │
│         │                    │ Recopilación     │
└────┬────┘                    └────────┬─────────┘
     │                                  │
     │ POST /api/v1/data/load/pre       │
     │ Authorization: Bearer <token>    │
     ├─────────────────────────────────>│
     │                                  │
     │                                  ├─ Validar token
     │                                  │
     │                                  ├─ Acceder a datos-pre/
     │                                  │
     │                                  ├─ Leer archivos CSV/XLS
     │                                  │
     │                                  ├─ Procesar cada archivo:
     │                                  │  - Contar registros
     │                                  │  - Extraer fechas min/max
     │                                  │
     │                                  ├─ Cargar en memoria/DB
     │                                  │
     │ 200 OK                           │
     │ {files: [...], total_records}    │
     │<─────────────────────────────────┤
     │                                  │
```

## Casos de Prueba

### CP01: Carga exitosa de múltiples archivos
- **Entrada:** 2 archivos (1 CSV, 1 XLSX) en datos-pre/
- **Resultado esperado:** 200 OK, listado de 2 archivos con metadatos

### CP02: Carga con carpeta vacía
- **Entrada:** Carpeta datos-pre/ vacía
- **Resultado esperado:** 404 Not Found

### CP03: Archivo CSV con formato incorrecto
- **Entrada:** CSV con columnas mal formadas
- **Resultado esperado:** 422 Unprocessable Entity

### CP04: Sin autenticación
- **Entrada:** Petición sin header Authorization
- **Resultado esperado:** 401 Unauthorized

### CP05: Diferentes formatos de fecha
- **Entrada:** CSV con fechas en DD/MM/YYYY
- **Resultado esperado:** 200 OK, fechas correctamente parseadas

## Notas Adicionales

- La carga es **no destructiva** por defecto (no borra datos existentes)
- Se puede usar el parámetro `clear_existing: true` para limpiar antes de cargar
- Los archivos permanecen en la carpeta después de la carga
- El sistema detecta automáticamente el delimitador en archivos CSV
- Se registra en logs cada operación de carga con timestamp y usuario
- En PRO, se recomienda hacer backup antes de cargar datos nuevos
- Los tests **siempre** deben ejecutarse contra PRE, nunca contra PRO
