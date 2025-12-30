# README - Tests de Integración

## Descripción

Este directorio contiene los tests de integración para los diferentes microservicios de la aplicación de análisis de gastos.

## Estructura

```
tests/
├── test_auth_service.py              # Tests del microservicio de autenticación
├── test_data_collection_service.py   # Tests del microservicio de recopilación de datos (pendiente)
└── test_data_manipulation_service.py # Tests del microservicio de manipulación de datos (pendiente)
```

## Microservicios

### Microservicio de Autenticación (Puerto 8001)
- **URL Base:** http://localhost:8001
- **Responsabilidad:** Autenticación y gestión de usuarios
- **Tests:** `test_auth_service.py`

### Microservicio de Recopilación de Datos (Puerto 8002) - Pendiente
- **URL Base:** http://localhost:8002
- **Responsabilidad:** Recopilación y almacenamiento de datos de gastos
- **Tests:** `test_data_collection_service.py`

### Microservicio de Manipulación de Datos (Puerto 8003) - Pendiente
- **URL Base:** http://localhost:8003
- **Responsabilidad:** Análisis y procesamiento de datos de gastos
- **Tests:** `test_data_manipulation_service.py`

## Instalación

Para instalar las dependencias necesarias para ejecutar los tests:

```bash
pip install -r requirements-test.txt
```

## Ejecución de Tests

### Ejecutar todos los tests
```bash
pytest tests/ -v
```

### Ejecutar tests de un microservicio específico
```bash
# Tests del microservicio de autenticación
pytest tests/test_auth_service.py -v

# Tests del microservicio de recopilación de datos
pytest tests/test_data_collection_service.py -v

# Tests del microservicio de manipulación de datos
pytest tests/test_data_manipulation_service.py -v
```

### Ejecutar un test específico
```bash
pytest tests/test_auth_service.py::TestLoginEndpoint::test_login_successful -v
```

### Ejecutar tests con cobertura
```bash
pytest tests/ --cov=. --cov-report=html
```

## Desarrollo Guiado por Pruebas (TDD)

Este proyecto sigue la metodología TDD (Test-Driven Development):

1. **Red (Rojo):** Escribir un test que falle
2. **Green (Verde):** Escribir el código mínimo para que el test pase
3. **Refactor:** Mejorar el código manteniendo los tests en verde

### Flujo de Trabajo

1. Crear o actualizar el caso de uso en `casos-de-uso/`
2. Escribir los tests de integración basados en el caso de uso
3. Ejecutar los tests y verificar que fallan (Red)
4. Implementar el microservicio correspondiente
5. Ejecutar los tests hasta que pasen (Green)
6. Refactorizar si es necesario
7. Repetir

## Notas Importantes

- Los tests están diseñados para fallar hasta que se implementen los microservicios correspondientes
- Asegúrate de que los microservicios estén corriendo antes de ejecutar los tests
- Los tests de integración requieren que los servicios estén disponibles en los puertos especificados
- Se recomienda usar entornos virtuales de Python para aislar las dependencias

## Estado Actual

- ✅ Tests del microservicio de autenticación (caso de uso 01: Login)
- ⏳ Tests del microservicio de recopilación de datos (pendiente)
- ⏳ Tests del microservicio de manipulación de datos (pendiente)
