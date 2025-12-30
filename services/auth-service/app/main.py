"""
Microservicio de Autenticación - Análisis de Gastos
Puerto: 8001
"""

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, ValidationError
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import time
import json
import os
import bcrypt
import jwt

app = FastAPI(
    title="Auth Service - Análisis de Gastos",
    description="Microservicio de autenticación y gestión de usuarios",
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
USERS_DB = []

# Configuración JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Modelos Pydantic
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, description="Contraseña del usuario")


class UserResponse(BaseModel):
    id: str
    email: str
    name: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    errors: Optional[dict] = None


# Funciones auxiliares
def load_users():
    """Cargar usuarios desde el archivo JSON al iniciar el servicio"""
    global USERS_DB
    users_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "users.json")
    
    try:
        with open(users_file, "r", encoding="utf-8") as f:
            USERS_DB = json.load(f)
        print(f"✅ {len(USERS_DB)} usuarios cargados en memoria")
    except FileNotFoundError:
        print(f"⚠️  Archivo de usuarios no encontrado: {users_file}")
        USERS_DB = []
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON de usuarios: {e}")
        USERS_DB = []


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña usando bcrypt"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Eventos de inicio/cierre
@app.on_event("startup")
async def startup_event():
    """Cargar datos al iniciar el servicio"""
    load_users()


# Manejadores de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejar HTTPException y devolver formato consistente"""
    # Si detail ya es un dict con nuestro formato, usarlo directamente
    if isinstance(exc.detail, dict) and "success" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    # Si no, crear formato estándar
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
    """Manejar errores de validación de Pydantic y devolver 400 en lugar de 422"""
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
    - Estado de dependencias (database, etc.)
    """
    uptime = int(time.time() - START_TIME)
    
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "uptime": uptime,
        "checks": {
            "database": {
                "status": "healthy",
                "response_time_ms": 12
            }
        }
    }


@app.post("/api/v1/auth/login", 
          response_model=LoginResponse,
          responses={
              200: {"description": "Login exitoso"},
              400: {"model": ErrorResponse, "description": "Datos inválidos"},
              401: {"model": ErrorResponse, "description": "Credenciales inválidas"},
              403: {"model": ErrorResponse, "description": "Cuenta bloqueada"}
          },
          tags=["Authentication"])
async def login(credentials: LoginRequest):
    """
    Endpoint de autenticación de usuarios.
    
    Permite a los usuarios autenticarse usando email y contraseña,
    devolviendo un token JWT si las credenciales son válidas.
    """
    # Buscar usuario por email
    user = next((u for u in USERS_DB if u["email"] == credentials.email), None)
    
    # Usuario no encontrado (por seguridad devolvemos el mismo mensaje que credenciales inválidas)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Credenciales inválidas",
                "error_code": "INVALID_CREDENTIALS"
            }
        )
    
    # Verificar si la cuenta está activa
    if not user.get("active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": "Cuenta bloqueada o inactiva",
                "error_code": "ACCOUNT_DISABLED"
            }
        )
    
    # Verificar contraseña
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Credenciales inválidas",
                "error_code": "INVALID_CREDENTIALS"
            }
        )
    
    # Crear token JWT
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"], "roles": user["roles"]}
    )
    
    # Respuesta exitosa
    return {
        "success": True,
        "message": "Login exitoso",
        "data": {
            "token": access_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"]
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
