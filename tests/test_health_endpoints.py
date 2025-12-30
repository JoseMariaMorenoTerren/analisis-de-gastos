"""
Tests de integración para los endpoints de health check de todos los microservicios.

Este módulo contiene las pruebas de integración para validar el comportamiento
de los endpoints de health check según el caso de uso 02: Health Check.
"""

import pytest
import requests
import time
from typing import Dict, Any


# Configuración de los microservicios
AUTH_SERVICE_URL = "http://localhost:8001"
DATA_COLLECTION_SERVICE_URL = "http://localhost:8002"
DATA_MANIPULATION_SERVICE_URL = "http://localhost:8003"

# Endpoints de health
AUTH_HEALTH_ENDPOINT = f"{AUTH_SERVICE_URL}/api/v1/health"
DATA_COLLECTION_HEALTH_ENDPOINT = f"{DATA_COLLECTION_SERVICE_URL}/api/v1/health"
DATA_MANIPULATION_HEALTH_ENDPOINT = f"{DATA_MANIPULATION_SERVICE_URL}/api/v1/health"


class TestAuthServiceHealth:
    """Tests para el endpoint de health check del microservicio de autenticación."""
    
    def test_health_endpoint_accessible(self):
        """
        Test: El endpoint de health debe ser accesible sin autenticación.
        
        Verifica que:
        - El endpoint responde sin requerir headers de autenticación
        - El endpoint es público
        """
        response = requests.get(AUTH_HEALTH_ENDPOINT)
        
        # El endpoint debe responder (200 o 503, pero no 401/403)
        assert response.status_code in [200, 503], \
            f"Se esperaba código 200 o 503, se obtuvo {response.status_code}"
        assert response.status_code != 401, \
            "El endpoint de health no debe requerir autenticación"
        assert response.status_code != 403, \
            "El endpoint de health debe ser público"
    
    def test_health_response_structure(self):
        """
        Test: La respuesta debe tener la estructura correcta.
        
        Verifica que:
        - Contiene los campos requeridos: status, service, version, timestamp, uptime, checks
        - Los tipos de datos son correctos
        """
        response = requests.get(AUTH_HEALTH_ENDPOINT)
        data = response.json()
        
        # Verificar campos requeridos
        assert "status" in data, "La respuesta debe contener 'status'"
        assert "service" in data, "La respuesta debe contener 'service'"
        assert "version" in data, "La respuesta debe contener 'version'"
        assert "timestamp" in data, "La respuesta debe contener 'timestamp'"
        assert "uptime" in data, "La respuesta debe contener 'uptime'"
        assert "checks" in data, "La respuesta debe contener 'checks'"
        
        # Verificar tipos de datos
        assert isinstance(data["status"], str), "'status' debe ser string"
        assert isinstance(data["service"], str), "'service' debe ser string"
        assert isinstance(data["version"], str), "'version' debe ser string"
        assert isinstance(data["timestamp"], str), "'timestamp' debe ser string"
        assert isinstance(data["uptime"], (int, float)), "'uptime' debe ser numérico"
        assert isinstance(data["checks"], dict), "'checks' debe ser un objeto"
        
        # Verificar que el servicio tiene el nombre correcto
        assert data["service"] == "auth-service", \
            "El nombre del servicio debe ser 'auth-service'"
    
    def test_health_status_values(self):
        """
        Test: El campo status debe tener uno de los valores permitidos.
        
        Verifica que:
        - El status es uno de: healthy, degraded, unhealthy, starting
        """
        response = requests.get(AUTH_HEALTH_ENDPOINT)
        data = response.json()
        
        valid_statuses = ["healthy", "degraded", "unhealthy", "starting"]
        assert data["status"] in valid_statuses, \
            f"El status debe ser uno de {valid_statuses}, se obtuvo '{data['status']}'"
    
    def test_health_checks_structure(self):
        """
        Test: El objeto checks debe tener la estructura correcta.
        
        Verifica que:
        - Cada check contiene al menos el campo 'status'
        - Los checks pueden incluir response_time_ms y error
        """
        response = requests.get(AUTH_HEALTH_ENDPOINT)
        data = response.json()
        
        checks = data["checks"]
        assert len(checks) > 0, "Debe haber al menos un check"
        
        for check_name, check_data in checks.items():
            assert "status" in check_data, \
                f"El check '{check_name}' debe contener 'status'"
            assert isinstance(check_data["status"], str), \
                f"El status del check '{check_name}' debe ser string"
            
            # Si existe response_time_ms, debe ser numérico o null
            if "response_time_ms" in check_data:
                assert check_data["response_time_ms"] is None or \
                       isinstance(check_data["response_time_ms"], (int, float)), \
                    f"El response_time_ms del check '{check_name}' debe ser numérico o null"
    
    def test_health_response_time(self):
        """
        Test: El endpoint debe responder rápidamente.
        
        Verifica que:
        - El tiempo de respuesta es inferior a 100ms (requisito no funcional)
        """
        start_time = time.time()
        response = requests.get(AUTH_HEALTH_ENDPOINT)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convertir a milisegundos
        
        assert response_time < 100, \
            f"El tiempo de respuesta ({response_time:.2f}ms) debe ser inferior a 100ms"
    
    def test_health_http_status_codes(self):
        """
        Test: El código HTTP debe corresponder con el status del servicio.
        
        Verifica que:
        - healthy/degraded -> 200 OK
        - unhealthy/starting -> 503 Service Unavailable
        """
        response = requests.get(AUTH_HEALTH_ENDPOINT)
        data = response.json()
        
        if data["status"] in ["healthy", "degraded"]:
            assert response.status_code == 200, \
                f"Un servicio '{data['status']}' debe devolver 200 OK"
        elif data["status"] in ["unhealthy", "starting"]:
            assert response.status_code == 503, \
                f"Un servicio '{data['status']}' debe devolver 503 Service Unavailable"
    
    def test_health_content_type(self):
        """
        Test: El Content-Type debe ser application/json.
        
        Verifica que:
        - El header Content-Type es application/json
        """
        response = requests.get(AUTH_HEALTH_ENDPOINT)
        
        assert "application/json" in response.headers.get("Content-Type", ""), \
            "El Content-Type debe ser application/json"
    
    def test_health_uptime_positive(self):
        """
        Test: El uptime debe ser un valor positivo.
        
        Verifica que:
        - El uptime es mayor que 0
        """
        response = requests.get(AUTH_HEALTH_ENDPOINT)
        data = response.json()
        
        assert data["uptime"] > 0, \
            f"El uptime ({data['uptime']}) debe ser mayor que 0"


class TestDataCollectionServiceHealth:
    """Tests para el endpoint de health check del microservicio de recopilación de datos."""
    
    def test_health_endpoint_accessible(self):
        """Test: El endpoint de health debe ser accesible sin autenticación."""
        response = requests.get(DATA_COLLECTION_HEALTH_ENDPOINT)
        
        assert response.status_code in [200, 503], \
            f"Se esperaba código 200 o 503, se obtuvo {response.status_code}"
        assert response.status_code != 401, \
            "El endpoint de health no debe requerir autenticación"
    
    def test_health_response_structure(self):
        """Test: La respuesta debe tener la estructura correcta."""
        response = requests.get(DATA_COLLECTION_HEALTH_ENDPOINT)
        data = response.json()
        
        assert "status" in data, "La respuesta debe contener 'status'"
        assert "service" in data, "La respuesta debe contener 'service'"
        assert "version" in data, "La respuesta debe contener 'version'"
        assert "timestamp" in data, "La respuesta debe contener 'timestamp'"
        assert "uptime" in data, "La respuesta debe contener 'uptime'"
        assert "checks" in data, "La respuesta debe contener 'checks'"
        
        assert data["service"] == "data-collection-service", \
            "El nombre del servicio debe ser 'data-collection-service'"
    
    def test_health_includes_database_check(self):
        """
        Test: Debe incluir verificación de base de datos.
        
        Verifica que:
        - Los checks incluyen al menos 'database'
        """
        response = requests.get(DATA_COLLECTION_HEALTH_ENDPOINT)
        data = response.json()
        
        checks = data["checks"]
        assert "database" in checks, \
            "Los checks deben incluir verificación de 'database'"
    
    def test_health_includes_auth_service_check(self):
        """
        Test: Debe incluir verificación del servicio de autenticación.
        
        Verifica que:
        - Los checks incluyen 'auth_service' (dependencia externa)
        """
        response = requests.get(DATA_COLLECTION_HEALTH_ENDPOINT)
        data = response.json()
        
        checks = data["checks"]
        assert "auth_service" in checks, \
            "Los checks deben incluir verificación de 'auth_service'"
    
    def test_health_response_time(self):
        """Test: El endpoint debe responder rápidamente (< 100ms)."""
        start_time = time.time()
        response = requests.get(DATA_COLLECTION_HEALTH_ENDPOINT)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response_time < 100, \
            f"El tiempo de respuesta ({response_time:.2f}ms) debe ser inferior a 100ms"


class TestDataManipulationServiceHealth:
    """Tests para el endpoint de health check del microservicio de manipulación de datos."""
    
    def test_health_endpoint_accessible(self):
        """Test: El endpoint de health debe ser accesible sin autenticación."""
        response = requests.get(DATA_MANIPULATION_HEALTH_ENDPOINT)
        
        assert response.status_code in [200, 503], \
            f"Se esperaba código 200 o 503, se obtuvo {response.status_code}"
        assert response.status_code != 401, \
            "El endpoint de health no debe requerir autenticación"
    
    def test_health_response_structure(self):
        """Test: La respuesta debe tener la estructura correcta."""
        response = requests.get(DATA_MANIPULATION_HEALTH_ENDPOINT)
        data = response.json()
        
        assert "status" in data, "La respuesta debe contener 'status'"
        assert "service" in data, "La respuesta debe contener 'service'"
        assert "version" in data, "La respuesta debe contener 'version'"
        assert "timestamp" in data, "La respuesta debe contener 'timestamp'"
        assert "uptime" in data, "La respuesta debe contener 'uptime'"
        assert "checks" in data, "La respuesta debe contener 'checks'"
        
        assert data["service"] == "data-manipulation-service", \
            "El nombre del servicio debe ser 'data-manipulation-service'"
    
    def test_health_includes_database_check(self):
        """Test: Debe incluir verificación de base de datos."""
        response = requests.get(DATA_MANIPULATION_HEALTH_ENDPOINT)
        data = response.json()
        
        checks = data["checks"]
        assert "database" in checks, \
            "Los checks deben incluir verificación de 'database'"
    
    def test_health_includes_data_collection_service_check(self):
        """
        Test: Debe incluir verificación del servicio de recopilación.
        
        Verifica que:
        - Los checks incluyen 'data_collection_service' (dependencia externa)
        """
        response = requests.get(DATA_MANIPULATION_HEALTH_ENDPOINT)
        data = response.json()
        
        checks = data["checks"]
        assert "data_collection_service" in checks, \
            "Los checks deben incluir verificación de 'data_collection_service'"
    
    def test_health_response_time(self):
        """Test: El endpoint debe responder rápidamente (< 100ms)."""
        start_time = time.time()
        response = requests.get(DATA_MANIPULATION_HEALTH_ENDPOINT)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response_time < 100, \
            f"El tiempo de respuesta ({response_time:.2f}ms) debe ser inferior a 100ms"


class TestHealthComparison:
    """Tests comparativos entre los health checks de todos los servicios."""
    
    def test_all_services_respond(self):
        """
        Test: Todos los servicios deben tener un endpoint de health funcional.
        
        Verifica que:
        - Los tres servicios responden al health check
        """
        services = [
            ("auth-service", AUTH_HEALTH_ENDPOINT),
            ("data-collection-service", DATA_COLLECTION_HEALTH_ENDPOINT),
            ("data-manipulation-service", DATA_MANIPULATION_HEALTH_ENDPOINT)
        ]
        
        for service_name, endpoint in services:
            try:
                response = requests.get(endpoint, timeout=5)
                assert response.status_code in [200, 503], \
                    f"{service_name}: Debe responder con 200 o 503"
            except requests.exceptions.RequestException as e:
                pytest.fail(f"{service_name}: No se pudo conectar al endpoint de health - {e}")
    
    def test_consistent_response_format(self):
        """
        Test: Todos los servicios deben usar el mismo formato de respuesta.
        
        Verifica que:
        - Todos tienen los mismos campos requeridos
        - El formato es consistente entre servicios
        """
        endpoints = [
            AUTH_HEALTH_ENDPOINT,
            DATA_COLLECTION_HEALTH_ENDPOINT,
            DATA_MANIPULATION_HEALTH_ENDPOINT
        ]
        
        required_fields = ["status", "service", "version", "timestamp", "uptime", "checks"]
        
        for endpoint in endpoints:
            response = requests.get(endpoint)
            data = response.json()
            
            for field in required_fields:
                assert field in data, \
                    f"El endpoint {endpoint} debe contener el campo '{field}'"
    
    def test_version_format(self):
        """
        Test: Todas las versiones deben seguir el formato semántico.
        
        Verifica que:
        - Las versiones tienen formato X.Y.Z (semántico)
        """
        import re
        
        endpoints = [
            AUTH_HEALTH_ENDPOINT,
            DATA_COLLECTION_HEALTH_ENDPOINT,
            DATA_MANIPULATION_HEALTH_ENDPOINT
        ]
        
        version_pattern = re.compile(r'^\d+\.\d+\.\d+$')
        
        for endpoint in endpoints:
            response = requests.get(endpoint)
            data = response.json()
            
            assert version_pattern.match(data["version"]), \
                f"La versión '{data['version']}' debe seguir el formato semántico (X.Y.Z)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
