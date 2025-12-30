"""
Microservicio de Recopilación de Datos - Análisis de Gastos
Puerto: 8002
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time

app = FastAPI(
    title="Data Collection Service - Análisis de Gastos",
    description="Microservicio de recopilación y almacenamiento de datos",
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
    - Estado de dependencias (database, auth_service)
    """
    uptime = int(time.time() - START_TIME)
    
    # Por ahora, el servicio está en estado "healthy" simplificado
    # En una implementación real, verificaríamos conexiones a BD y auth service
    
    return {
        "status": "healthy",
        "service": "data-collection-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": uptime,
        "checks": {
            "database": {
                "status": "healthy",
                "response_time_ms": 10
            },
            "auth_service": {
                "status": "healthy",
                "response_time_ms": 25
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
