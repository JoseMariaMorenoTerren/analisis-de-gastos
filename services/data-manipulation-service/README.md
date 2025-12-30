# Data Manipulation Service

Microservicio de procesamiento y análisis de datos para el sistema de análisis de gastos.

## Puerto
8003

## Endpoints disponibles

### Health Check
- **GET** `/api/v1/health` - Verificación de salud del servicio

## Ejecutar el servicio

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python app/main.py
```

O usando uvicorn directamente:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

## Documentación API
Una vez ejecutado, visita:
- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc
