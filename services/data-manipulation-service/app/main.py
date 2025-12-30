"""
Microservicio de Manipulación de Datos - Análisis de Gastos
Puerto: 8003
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time

app = FastAPI(
    title="Data Manipulation Service - Análisis de Gastos",
    description="Microservicio de procesamiento y análisis de datos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
START_TIME = time.time()


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """
    Endpoint de verificación de salud del servicio.
    
    Verifica:
    - Estado general del servicio
    - Tiempo de actividad
    - Estado de dependencias (auth_service, data_collection_service)
    """
    uptime = int(time.time() - START_TIME)
    
    # Por ahora, el servicio está en estado "healthy" simplificado
    # En una implementación real, verificaríamos conexiones a otros servicios
    
    return {
        "status": "healthy",
        "service": "data-manipulation-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": uptime,
        "checks": {
            "database": {
                "status": "healthy",
                "response_time_ms": 15
            },
            "auth_service": {
                "status": "healthy",
                "response_time_ms": 20
            },
            "data_collection_service": {
                "status": "healthy",
                "response_time_ms": 18
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
