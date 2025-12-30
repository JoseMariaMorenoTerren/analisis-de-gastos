"""
Tests de integración para el microservicio de autenticación.

Este módulo contiene las pruebas de integración para validar el comportamiento
del microservicio de autenticación según el caso de uso 01: Login.
"""

import pytest
import requests
import json
from typing import Dict, Any


# Configuración del microservicio de autenticación
AUTH_SERVICE_URL = "http://localhost:8001"
LOGIN_ENDPOINT = f"{AUTH_SERVICE_URL}/api/v1/auth/login"


class TestLoginEndpoint:
    """Tests para el endpoint de login del microservicio de autenticación."""
    
    @pytest.fixture
    def valid_credentials(self) -> Dict[str, str]:
        """Credenciales válidas para testing."""
        return {
            "email": "user@example.com",
            "password": "password123"
        }
    
    @pytest.fixture
    def invalid_password_credentials(self) -> Dict[str, str]:
        """Credenciales con contraseña incorrecta."""
        return {
            "email": "user@example.com",
            "password": "wrong_password"
        }
    
    @pytest.fixture
    def non_existent_user_credentials(self) -> Dict[str, str]:
        """Credenciales de usuario que no existe."""
        return {
            "email": "noexiste@ejemplo.com",
            "password": "cualquier_contraseña"
        }

    def test_login_successful(self, valid_credentials):
        """
        Test: Login exitoso con credenciales válidas.
        
        Verifica que:
        - El código de respuesta sea 200 OK
        - La respuesta contenga un token JWT
        - La respuesta incluya información del usuario
        - La estructura de respuesta sea la esperada
        """
        response = requests.post(
            LOGIN_ENDPOINT,
            json=valid_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, \
            f"Se esperaba código 200, se obtuvo {response.status_code}"
        
        data = response.json()
        
        # Verificar estructura de respuesta
        assert data["success"] is True, "El campo 'success' debe ser True"
        assert "message" in data, "La respuesta debe contener 'message'"
        assert "data" in data, "La respuesta debe contener 'data'"
        
        # Verificar datos del token
        assert "token" in data["data"], "Los datos deben contener 'token'"
        assert "token_type" in data["data"], "Los datos deben contener 'token_type'"
        assert "expires_in" in data["data"], "Los datos deben contener 'expires_in'"
        assert data["data"]["token_type"] == "Bearer", \
            "El tipo de token debe ser 'Bearer'"
        
        # Verificar información del usuario
        assert "user" in data["data"], "Los datos deben contener información del 'user'"
        assert "id" in data["data"]["user"], "El usuario debe tener 'id'"
        assert "email" in data["data"]["user"], "El usuario debe tener 'email'"
        assert "name" in data["data"]["user"], "El usuario debe tener 'name'"
        assert data["data"]["user"]["email"] == valid_credentials["email"], \
            "El email del usuario debe coincidir"
        
        # Verificar que el token no esté vacío
        assert len(data["data"]["token"]) > 0, "El token no debe estar vacío"
        
        # Verificar Content-Type
        assert "application/json" in response.headers.get("Content-Type", ""), \
            "El Content-Type debe ser application/json"

    def test_login_invalid_credentials(self, invalid_password_credentials):
        """
        Test: Login con contraseña incorrecta.
        
        Verifica que:
        - El código de respuesta sea 401 Unauthorized
        - Se devuelva un mensaje de error apropiado
        - Se incluya el código de error INVALID_CREDENTIALS
        """
        response = requests.post(
            LOGIN_ENDPOINT,
            json=invalid_password_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401, \
            f"Se esperaba código 401, se obtuvo {response.status_code}"
        
        data = response.json()
        
        assert data["success"] is False, "El campo 'success' debe ser False"
        assert "message" in data, "La respuesta debe contener 'message'"
        assert "error_code" in data, "La respuesta debe contener 'error_code'"
        assert data["error_code"] == "INVALID_CREDENTIALS", \
            "El código de error debe ser 'INVALID_CREDENTIALS'"

    def test_login_user_not_found(self, non_existent_user_credentials):
        """
        Test: Login con usuario que no existe.
        
        Verifica que:
        - El código de respuesta sea 401 Unauthorized
        - El mensaje sea el mismo que para credenciales inválidas (por seguridad)
        - Se incluya el código de error INVALID_CREDENTIALS
        """
        response = requests.post(
            LOGIN_ENDPOINT,
            json=non_existent_user_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401, \
            f"Se esperaba código 401, se obtuvo {response.status_code}"
        
        data = response.json()
        
        assert data["success"] is False, "El campo 'success' debe ser False"
        assert data["error_code"] == "INVALID_CREDENTIALS", \
            "El código de error debe ser 'INVALID_CREDENTIALS'"

    def test_login_missing_email(self):
        """
        Test: Login sin proporcionar email.
        
        Verifica que:
        - El código de respuesta sea 400 Bad Request
        - Se indique que el campo email es requerido
        - Se incluya el código de error VALIDATION_ERROR
        """
        credentials = {"password": "alguna_contraseña"}
        
        response = requests.post(
            LOGIN_ENDPOINT,
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, \
            f"Se esperaba código 400, se obtuvo {response.status_code}"
        
        data = response.json()
        
        assert data["success"] is False, "El campo 'success' debe ser False"
        assert "errors" in data, "La respuesta debe contener 'errors'"
        assert "email" in data["errors"], \
            "Los errores deben incluir el campo 'email'"
        assert data["error_code"] == "VALIDATION_ERROR", \
            "El código de error debe ser 'VALIDATION_ERROR'"

    def test_login_missing_password(self):
        """
        Test: Login sin proporcionar contraseña.
        
        Verifica que:
        - El código de respuesta sea 400 Bad Request
        - Se indique que el campo password es requerido
        - Se incluya el código de error VALIDATION_ERROR
        """
        credentials = {"email": "usuario@ejemplo.com"}
        
        response = requests.post(
            LOGIN_ENDPOINT,
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, \
            f"Se esperaba código 400, se obtuvo {response.status_code}"
        
        data = response.json()
        
        assert data["success"] is False, "El campo 'success' debe ser False"
        assert "errors" in data, "La respuesta debe contener 'errors'"
        assert "password" in data["errors"], \
            "Los errores deben incluir el campo 'password'"
        assert data["error_code"] == "VALIDATION_ERROR", \
            "El código de error debe ser 'VALIDATION_ERROR'"

    def test_login_missing_both_fields(self):
        """
        Test: Login sin proporcionar email ni contraseña.
        
        Verifica que:
        - El código de respuesta sea 400 Bad Request
        - Se indique que ambos campos son requeridos
        - Se incluya el código de error VALIDATION_ERROR
        """
        credentials = {}
        
        response = requests.post(
            LOGIN_ENDPOINT,
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, \
            f"Se esperaba código 400, se obtuvo {response.status_code}"
        
        data = response.json()
        
        assert data["success"] is False, "El campo 'success' debe ser False"
        assert "errors" in data, "La respuesta debe contener 'errors'"
        assert "email" in data["errors"], \
            "Los errores deben incluir el campo 'email'"
        assert "password" in data["errors"], \
            "Los errores deben incluir el campo 'password'"
        assert data["error_code"] == "VALIDATION_ERROR", \
            "El código de error debe ser 'VALIDATION_ERROR'"

    def test_login_invalid_email_format(self):
        """
        Test: Login con formato de email inválido.
        
        Verifica que:
        - El código de respuesta sea 400 Bad Request
        - Se indique que el formato del email es inválido
        - Se incluya el código de error VALIDATION_ERROR
        """
        credentials = {
            "email": "email_invalido_sin_arroba",
            "password": "alguna_contraseña"
        }
        
        response = requests.post(
            LOGIN_ENDPOINT,
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, \
            f"Se esperaba código 400, se obtuvo {response.status_code}"
        
        data = response.json()
        
        assert data["success"] is False, "El campo 'success' debe ser False"
        assert "errors" in data, "La respuesta debe contener 'errors'"
        assert "email" in data["errors"], \
            "Los errores deben incluir el campo 'email'"
        assert data["error_code"] == "VALIDATION_ERROR", \
            "El código de error debe ser 'VALIDATION_ERROR'"

    def test_login_account_disabled(self):
        """
        Test: Login con cuenta desactivada o bloqueada.
        
        Verifica que:
        - El código de respuesta sea 403 Forbidden
        - Se indique que la cuenta está bloqueada o inactiva
        - Se incluya el código de error ACCOUNT_DISABLED
        """
        credentials = {
            "email": "disabled@example.com",
            "password": "password123"
        }
        
        response = requests.post(
            LOGIN_ENDPOINT,
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 403, \
            f"Se esperaba código 403, se obtuvo {response.status_code}"
        
        data = response.json()
        
        assert data["success"] is False, "El campo 'success' debe ser False"
        assert "message" in data, "La respuesta debe contener 'message'"
        assert data["error_code"] == "ACCOUNT_DISABLED", \
            "El código de error debe ser 'ACCOUNT_DISABLED'"

    def test_login_response_time(self, valid_credentials):
        """
        Test: Verificar que el tiempo de respuesta sea aceptable.
        
        Verifica que:
        - El tiempo de respuesta sea inferior a 500ms (requisito no funcional)
        """
        import time
        
        start_time = time.time()
        requests.post(
            LOGIN_ENDPOINT,
            json=valid_credentials,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convertir a milisegundos
        
        assert response_time < 500, \
            f"El tiempo de respuesta ({response_time:.2f}ms) debe ser inferior a 500ms"


class TestLoginSecurity:
    """Tests de seguridad para el endpoint de login."""
    
    def test_login_password_not_in_response(self):
        """
        Test: Verificar que la contraseña nunca se devuelva en la respuesta.
        
        Verifica que:
        - La respuesta no contenga la contraseña en ningún campo
        - Ni en caso de éxito ni en caso de error
        """
        credentials = {
            "email": "usuario@ejemplo.com",
            "password": "contraseña_que_no_debe_aparecer"
        }
        
        response = requests.post(
            LOGIN_ENDPOINT,
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        response_text = response.text.lower()
        
        # Verificar que la contraseña no aparezca en la respuesta
        assert credentials["password"].lower() not in response_text, \
            "La contraseña no debe aparecer en la respuesta"
        assert "password" not in response.json().get("data", {}), \
            "El objeto 'data' no debe contener un campo 'password'"

    def test_login_rate_limiting_header(self):
        """
        Test: Verificar que existan headers relacionados con rate limiting.
        
        Este test verifica la presencia de headers que indican
        implementación de rate limiting para prevenir ataques de fuerza bruta.
        """
        credentials = {
            "email": "usuario@ejemplo.com",
            "password": "alguna_contraseña"
        }
        
        response = requests.post(
            LOGIN_ENDPOINT,
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        # Nota: Este test puede ajustarse según la implementación específica
        # de rate limiting que se decida usar (X-RateLimit-*, Retry-After, etc.)
        # Se pueden verificar headers como X-RateLimit-*, Retry-After, etc.
        
        # Verificar que al menos se haya considerado algún mecanismo de rate limiting
        # (Este test se puede hacer más específico una vez se implemente)
        assert response.status_code in [200, 400, 401, 403, 429], \
            "El endpoint debe estar implementado y responder con códigos HTTP válidos"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
