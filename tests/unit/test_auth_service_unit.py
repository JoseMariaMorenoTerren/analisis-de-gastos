"""
Tests unitarios para el microservicio de autenticación.

Estos tests prueban las funciones y lógica interna del servicio
importando directamente los módulos, lo que permite generar
métricas de cobertura de código (coverage).
"""

import pytest
import sys
import os
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from pathlib import Path

# Agregar el directorio del servicio al path
service_path = Path(__file__).parent.parent.parent / "services" / "auth-service" / "app"
sys.path.insert(0, str(service_path))

# Importar funciones del servicio
import main
verify_password = main.verify_password
create_access_token = main.create_access_token
load_users = main.load_users
SECRET_KEY = main.SECRET_KEY
ALGORITHM = main.ALGORITHM


class TestPasswordVerification:
    """Tests unitarios para verificación de contraseñas."""
    
    def test_verify_password_correct(self):
        """Test: Verificar contraseña correcta."""
        # Hash generado para 'password123'
        hashed = "$2b$12$pg9r6ywPRdvUWj8WLqvO4O2hqI3gsfeLWmKg9UlQpUZyjM.kN5Aoq"
        
        result = verify_password("password123", hashed)
        assert result is True, "Debería verificar la contraseña correcta"
    
    def test_verify_password_incorrect(self):
        """Test: Verificar contraseña incorrecta."""
        hashed = "$2b$12$pg9r6ywPRdvUWj8WLqvO4O2hqI3gsfeLWmKg9UlQpUZyjM.kN5Aoq"
        
        result = verify_password("wrong_password", hashed)
        assert result is False, "Debería rechazar la contraseña incorrecta"
    
    def test_verify_password_empty(self):
        """Test: Verificar con contraseña vacía."""
        hashed = "$2b$12$pg9r6ywPRdvUWj8WLqvO4O2hqI3gsfeLWmKg9UlQpUZyjM.kN5Aoq"
        
        result = verify_password("", hashed)
        assert result is False, "Debería rechazar contraseña vacía"


class TestJWTTokens:
    """Tests unitarios para generación de tokens JWT."""
    
    def test_create_access_token(self):
        """Test: Crear token JWT con datos válidos."""
        data = {
            "sub": "user@example.com",
            "user_id": "123",
            "roles": ["user"]
        }
        
        token = create_access_token(data)
        
        assert token is not None, "El token no debería ser None"
        assert isinstance(token, str), "El token debería ser una cadena"
        assert len(token) > 0, "El token no debería estar vacío"
    
    def test_token_contains_correct_data(self):
        """Test: El token contiene los datos correctos."""
        data = {
            "sub": "admin@example.com",
            "user_id": "456",
            "roles": ["admin"]
        }
        
        token = create_access_token(data)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded["sub"] == "admin@example.com", "El email debería coincidir"
        assert decoded["user_id"] == "456", "El user_id debería coincidir"
        assert decoded["roles"] == ["admin"], "Los roles deberían coincidir"
    
    def test_token_has_expiration(self):
        """Test: El token tiene tiempo de expiración."""
        data = {"sub": "user@example.com"}
        
        token = create_access_token(data)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert "exp" in decoded, "El token debería tener campo 'exp'"
        
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # El token debería expirar en el futuro
        assert exp_time > now, "La expiración debería ser en el futuro"
        
        # Debería expirar en aproximadamente 60 minutos
        time_diff = (exp_time - now).total_seconds()
        assert 3500 < time_diff < 3700, "Debería expirar en ~60 minutos"
    
    def test_token_with_custom_expiration(self):
        """Test: Crear token con expiración personalizada."""
        data = {"sub": "user@example.com"}
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(data, expires_delta=expires_delta)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        time_diff = (exp_time - now).total_seconds()
        assert 1700 < time_diff < 1900, "Debería expirar en ~30 minutos"


class TestUserLoading:
    """Tests unitarios para carga de usuarios."""
    
    def test_load_users_populates_database(self):
        """Test: load_users carga usuarios en USERS_DB."""
        # Guardar estado original
        import main
        original_users = main.USERS_DB.copy()
        
        # Limpiar y cargar
        main.USERS_DB = []
        load_users()
        
        # Verificar que se cargaron usuarios
        assert len(main.USERS_DB) > 0, "Debería haber usuarios cargados"
        
        # Restaurar estado original
        main.USERS_DB = original_users
    
    def test_loaded_users_have_required_fields(self):
        """Test: Los usuarios cargados tienen los campos requeridos."""
        import main
        
        # Asegurarse de que hay usuarios
        if len(main.USERS_DB) == 0:
            load_users()
        
        required_fields = ["id", "email", "name", "password_hash", "roles", "active"]
        
        for user in main.USERS_DB:
            for field in required_fields:
                assert field in user, f"El usuario debería tener el campo '{field}'"
    
    def test_loaded_users_have_valid_email(self):
        """Test: Los usuarios tienen emails válidos."""
        import main
        
        if len(main.USERS_DB) == 0:
            load_users()
        
        for user in main.USERS_DB:
            email = user.get("email", "")
            assert "@" in email, f"El email '{email}' debería contener '@'"
            assert "." in email, f"El email '{email}' debería contener '.'"


class TestBcryptIntegration:
    """Tests para asegurar que bcrypt funciona correctamente."""
    
    def test_bcrypt_hash_and_verify(self):
        """Test: Generar y verificar hash con bcrypt."""
        password = "test_password_123"
        
        # Generar hash
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
        
        # Verificar que funciona
        assert bcrypt.checkpw(password.encode('utf-8'), hashed), \
            "bcrypt debería verificar la contraseña correcta"
        
        # Verificar que rechaza incorrecta
        assert not bcrypt.checkpw(b"wrong", hashed), \
            "bcrypt debería rechazar contraseña incorrecta"
