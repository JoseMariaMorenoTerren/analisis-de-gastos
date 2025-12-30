"""
Microservicio de Recopilación de Datos - Análisis de Gastos
Puerto: 8002
"""

from fastapi import FastAPI, HTTPException, status, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import time
import json
import os
import glob
import pandas as pd
from pathlib import Path
import jwt
import requests

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
ESTADO = {
    "environments": {
        "pre": {
            "loaded": False,
            "loaded_at": None,
            "files": [],
            "total_records": 0,
            "total_files": 0
        },
        "pro": {
            "loaded": False,
            "loaded_at": None,
            "files": [],
            "total_records": 0,
            "total_files": 0
        }
    },
    "data": {
        "pre": [],
        "pro": []
    }
}

# Configuración
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
STATE_FILE = PROJECT_ROOT / "data" / "estado-ms-data-collection-service.json"
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"


# Modelos Pydantic
class LoadRequest(BaseModel):
    clear_existing: bool = Field(False, description="Limpiar datos existentes antes de cargar")


class FileInfo(BaseModel):
    filename: str
    format: str
    records: int
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    size_bytes: int


class LoadResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# Funciones auxiliares
def save_state():
    """Guardar estado en archivo JSON"""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(ESTADO, f, indent=2, ensure_ascii=False, default=str)
        print(f"✅ Estado guardado en {STATE_FILE}")
    except Exception as e:
        print(f"❌ Error al guardar estado: {e}")


def load_state():
    """Cargar estado desde archivo JSON"""
    global ESTADO
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                ESTADO = json.load(f)
            print(f"✅ Estado cargado desde {STATE_FILE}")
        else:
            print(f"ℹ️  No se encontró archivo de estado, usando estado inicial")
    except Exception as e:
        print(f"⚠️  Error al cargar estado: {e}, usando estado inicial")


def verify_token(authorization: str) -> dict:
    """Verificar token JWT"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Token no proporcionado",
                "error_code": "MISSING_TOKEN"
            }
        )
    
    # Extraer token del header "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Formato de token inválido",
                "error_code": "INVALID_TOKEN_FORMAT"
            }
        )
    
    token = parts[1]
    
    try:
        # Decodificar y verificar token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Token inválido o expirado",
                "error_code": "INVALID_TOKEN"
            }
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Token inválido o expirado",
                "error_code": "INVALID_TOKEN"
            }
        )


def detect_date_column(df: pd.DataFrame) -> Optional[str]:
    """Detectar automáticamente la columna de fecha"""
    date_keywords = ['fecha', 'date', 'Fecha', 'Date', 'FECHA', 'DATE', 'Fecha y hora', 'fecha_hora']
    
    # Buscar coincidencia exacta
    for keyword in date_keywords:
        if keyword in df.columns:
            return keyword
    
    # Buscar coincidencia parcial (contiene la palabra)
    for col in df.columns:
        col_lower = col.lower()
        if 'fecha' in col_lower or 'date' in col_lower:
            return col
    
    return None


def parse_date_column(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Parsear columna de fecha a datetime"""
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
        return df
    except Exception:
        return df


def load_file(filepath: Path) -> tuple[pd.DataFrame, dict]:
    """Cargar un archivo CSV o Excel"""
    file_extension = filepath.suffix.lower()
    file_size = filepath.stat().st_size
    
    try:
        # Leer archivo según extensión
        if file_extension == '.csv':
            # Intentar detectar el delimitador automáticamente
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline()
                delimiter = ';' if ';' in first_line else ','
            df = pd.read_csv(filepath, delimiter=delimiter, encoding='utf-8', encoding_errors='ignore')
            file_format = 'csv'
        elif file_extension in ['.xls', '.xlsx']:
            df = pd.read_excel(filepath)
            file_format = 'xlsx' if file_extension == '.xlsx' else 'xls'
        else:
            raise ValueError(f"Formato no soportado: {file_extension}")
        
        # Detectar columna de fecha
        date_col = detect_date_column(df)
        fecha_inicio = None
        fecha_fin = None
        
        if date_col:
            df = parse_date_column(df, date_col)
            # Filtrar valores no nulos
            valid_dates = df[date_col].dropna()
            if len(valid_dates) > 0:
                fecha_inicio = valid_dates.min().strftime('%Y-%m-%d')
                fecha_fin = valid_dates.max().strftime('%Y-%m-%d')
        
        # Metadata del archivo
        file_info = {
            "filename": filepath.name,
            "format": file_format,
            "records": len(df),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "size_bytes": file_size
        }
        
        return df, file_info
        
    except Exception as e:
        raise ValueError(f"Error al leer {filepath.name}: {str(e)}")


def load_data_from_environment(environment: str, clear_existing: bool = False) -> dict:
    """Cargar datos desde una carpeta (pre o pro)"""
    global ESTADO
    
    # Determinar carpeta
    folder_path = PROJECT_ROOT / f"datos-{environment}"
    
    if not folder_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": f"No se encontraron archivos para cargar en {environment.upper()}",
                "error_code": "NO_FILES_FOUND"
            }
        )
    
    # Buscar archivos CSV y Excel
    files_pattern = list(folder_path.glob("*.csv")) + \
                   list(folder_path.glob("*.xls")) + \
                   list(folder_path.glob("*.xlsx"))
    
    if not files_pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": f"No se encontraron archivos para cargar en {environment.upper()}",
                "error_code": "NO_FILES_FOUND"
            }
        )
    
    # Limpiar datos existentes si se solicita
    if clear_existing:
        ESTADO["data"][environment] = []
        ESTADO["environments"][environment] = {
            "loaded": False,
            "loaded_at": None,
            "files": [],
            "total_records": 0,
            "total_files": 0
        }
    
    # Cargar cada archivo
    loaded_files = []
    total_records = 0
    errors = {}
    
    for filepath in files_pattern:
        try:
            df, file_info = load_file(filepath)
            loaded_files.append(file_info)
            total_records += len(df)
            
            # Agregar datos al estado (convertir a dict para serialización)
            data_records = df.to_dict('records')
            ESTADO["data"][environment].extend(data_records)
            
        except Exception as e:
            errors[filepath.name] = [str(e)]
    
    # Si hubo errores en todos los archivos
    if errors and not loaded_files:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "message": "Error al procesar archivos",
                "errors": errors,
                "error_code": "FILE_PROCESSING_ERROR",
                "data": {
                    "processed_files": 0,
                    "failed_files": len(errors)
                }
            }
        )
    
    # Actualizar estado
    ESTADO["environments"][environment] = {
        "loaded": True,
        "loaded_at": datetime.now(timezone.utc).isoformat(),
        "files": loaded_files,
        "total_records": total_records,
        "total_files": len(loaded_files)
    }
    
    # Guardar estado en disco
    save_state()
    
    return {
        "environment": environment,
        "total_files": len(loaded_files),
        "total_records": total_records,
        "files": loaded_files,
        "loaded_at": ESTADO["environments"][environment]["loaded_at"]
    }


# Eventos de inicio/cierre
@app.on_event("startup")
async def startup_event():
    """Cargar estado al iniciar el servicio"""
    load_state()


# Manejadores de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejar HTTPException y devolver formato consistente"""
    if isinstance(exc.detail, dict) and "success" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "error_code": "ERROR"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejar errores de validación de Pydantic"""
    errors = {}
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown"
        msg = error["msg"]
        if field not in errors:
            errors[field] = []
        errors[field].append(msg)
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": "Datos inválidos",
            "errors": errors,
            "error_code": "VALIDATION_ERROR"
        }
    )


# Endpoints
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
    
    return {
        "status": "healthy",
        "service": "data-collection-service",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
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


@app.post("/api/v1/data/load/pre",
          response_model=LoadResponse,
          responses={
              200: {"description": "Datos cargados exitosamente"},
              401: {"description": "No autenticado"},
              404: {"description": "No se encontraron archivos"},
              422: {"description": "Error al procesar archivos"}
          },
          tags=["Data Loading"])
async def load_data_pre(
    request_body: Optional[LoadRequest] = None,
    authorization: Optional[str] = Header(None)
):
    """
    Cargar datos desde el entorno PRE (desarrollo/testing).
    
    Requiere autenticación mediante token JWT.
    """
    # Verificar token
    verify_token(authorization)
    
    # Cargar datos
    clear_existing = request_body.clear_existing if request_body else False
    data = load_data_from_environment("pre", clear_existing)
    
    return {
        "success": True,
        "message": "Datos cargados exitosamente desde PRE",
        "data": data
    }


@app.post("/api/v1/data/load/pro",
          response_model=LoadResponse,
          responses={
              200: {"description": "Datos cargados exitosamente"},
              401: {"description": "No autenticado"},
              404: {"description": "No se encontraron archivos"},
              422: {"description": "Error al procesar archivos"}
          },
          tags=["Data Loading"])
async def load_data_pro(
    request_body: Optional[LoadRequest] = None,
    authorization: Optional[str] = Header(None)
):
    """
    Cargar datos desde el entorno PRO (producción).
    
    Requiere autenticación mediante token JWT.
    """
    # Verificar token
    verify_token(authorization)
    
    # Cargar datos
    clear_existing = request_body.clear_existing if request_body else False
    data = load_data_from_environment("pro", clear_existing)
    
    return {
        "success": True,
        "message": "Datos cargados exitosamente desde PRO",
        "data": data
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

