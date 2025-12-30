# Auth Service

Microservicio de autenticación para el sistema de análisis de gastos.

## Puerto
8001

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
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Documentación API
Una vez ejecutado, visita:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
