# Data Extraction Service

Microservicio de extracción y procesamiento de datos desde archivos para el sistema de análisis de gastos.

## Puerto
8004

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
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

## Documentación API
Una vez ejecutado, visita:
- Swagger UI: http://localhost:8004/docs
- ReDoc: http://localhost:8004/redoc

## Responsabilidades

Este servicio se encarga de:
- Leer archivos CSV y Excel desde el sistema de archivos
- Extraer y validar datos de gastos
- Transformar datos a formato estructurado
- Proporcionar datos procesados a otros servicios
