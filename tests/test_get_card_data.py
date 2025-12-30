"""
Tests de integración para el endpoint de obtención de datos de tarjetas.

Este módulo contiene las pruebas de integración para el endpoint GET /api/v1/data/cards
que devuelve todos los registros de archivos CSV concatenados con soporte de paginación.

Casos de prueba:
- Autenticación requerida
- Validación de parámetros (environment, page, page_size)
- Estructura de respuesta
- Metadatos de paginación
- Ordenamiento de datos
- Manejo de entornos sin datos

Microservicio: Data Collection Service (Puerto 8002)
Caso de uso: 05-obtener-datos-tarjetas.md
"""

import pytest
import requests

# Configuración de endpoints
BASE_URL = "http://localhost:8002"
CARD_DATA_ENDPOINT = f"{BASE_URL}/api/v1/data/cards"
LOGIN_ENDPOINT = "http://localhost:8001/api/v1/auth/login"

# Credenciales de prueba
TEST_CREDENTIALS = {
    "username": "test_user",
    "password": "test_password_123"
}


@pytest.fixture(scope="module")
def auth_headers():
    """
    Fixture para obtener headers de autenticación válidos.
    
    Returns:
        dict: Headers con el token Bearer
    """
    response = requests.post(LOGIN_ENDPOINT, json=TEST_CREDENTIALS)
    token = response.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


class TestGetCardDataAuthentication:
    """
    Tests relacionados con la autenticación del endpoint.
    """
    
    def test_get_card_data_requires_authentication(self):
        """
        Test: El endpoint debe requerir autenticación.
        
        Verifica que:
        - Sin token devuelve 401
        - El mensaje de error indica falta de token
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre"}
        )
        
        assert response.status_code == 401, \
            "Sin autenticación debe devolver 401"
        
        data = response.json()
        assert data["success"] is False, \
            "success debe ser false"
        assert "MISSING_TOKEN" in data["error"]["code"] or "UNAUTHORIZED" in data["error"]["code"], \
            "El código de error debe indicar token faltante"


class TestGetCardDataParameters:
    """
    Tests relacionados con la validación de parámetros.
    """
    
    def test_get_card_data_requires_environment_parameter(self, auth_headers):
        """
        Test: El parámetro environment es obligatorio.
        
        Verifica que:
        - Sin parámetro environment devuelve 400
        - El error indica parámetro faltante
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            headers=auth_headers
        )
        
        assert response.status_code == 400, \
            "Sin environment debe devolver 400"
        
        data = response.json()
        assert data["success"] is False, \
            "success debe ser false"
        assert data["error"]["code"] == "MISSING_PARAMETER", \
            "El código debe ser MISSING_PARAMETER"
        assert "environment" in data["error"]["message"].lower(), \
            "El mensaje debe mencionar 'environment'"
    
    def test_get_card_data_invalid_environment(self, auth_headers):
        """
        Test: El parámetro environment solo acepta 'pre' o 'pro'.
        
        Verifica que:
        - environment='invalid' devuelve 400
        - El error indica environment inválido
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "invalid"},
            headers=auth_headers
        )
        
        assert response.status_code == 400, \
            "Environment inválido debe devolver 400"
        
        data = response.json()
        assert data["success"] is False, \
            "success debe ser false"
        assert data["error"]["code"] == "INVALID_ENVIRONMENT", \
            "El código debe ser INVALID_ENVIRONMENT"
    
    def test_get_card_data_invalid_page_size(self, auth_headers):
        """
        Test: El page_size debe estar entre 1 y 2000.
        
        Verifica que:
        - page_size=3000 devuelve 400
        - page_size=0 devuelve 400
        - El error indica page_size inválido
        """
        # page_size mayor al máximo
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre", "page_size": 3000},
            headers=auth_headers
        )
        
        assert response.status_code == 400, \
            "page_size=3000 debe devolver 400"
        
        data = response.json()
        assert data["error"]["code"] == "INVALID_PAGE_SIZE", \
            "El código debe ser INVALID_PAGE_SIZE"
        
        # page_size cero
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre", "page_size": 0},
            headers=auth_headers
        )
        
        assert response.status_code == 400, \
            "page_size=0 debe devolver 400"


class TestGetCardDataPRE:
    """
    Tests para obtener datos del entorno PRE.
    """
    
    def test_get_card_data_pre_success(self, auth_headers):
        """
        Test: Obtener datos de PRE devuelve 200 con estructura correcta.
        
        Verifica que:
        - Devuelve status 200
        - success = true
        - Incluye data.environment, data.pagination, data.records
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre"},
            headers=auth_headers
        )
        
        assert response.status_code == 200, \
            "La petición debe ser exitosa"
        
        data = response.json()
        assert data["success"] is True, \
            "success debe ser true"
        assert "data" in data, \
            "Debe incluir el campo 'data'"
        
        card_data = data["data"]
        assert card_data["environment"] == "pre", \
            "El entorno debe ser 'pre'"
        assert "pagination" in card_data, \
            "Debe incluir metadatos de paginación"
        assert "records" in card_data, \
            "Debe incluir el array de registros"
        assert "retrieved_at" in card_data, \
            "Debe incluir timestamp"
    
    def test_get_card_data_pre_has_correct_record_count(self, auth_headers):
        """
        Test: PRE debe tener 230 registros totales del archivo CSV.
        
        Verifica que:
        - total_records = 230
        - El array records tiene <= 230 elementos (según page_size)
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre"},
            headers=auth_headers
        )
        
        data = response.json()
        pagination = data["data"]["pagination"]
        
        assert pagination["total_records"] == 230, \
            f"PRE debe tener 230 registros (del archivo CSV), tiene {pagination['total_records']}"
        
        records = data["data"]["records"]
        assert len(records) <= 230, \
            "El array de registros no puede tener más de 230 elementos"
    
    def test_get_card_data_pre_default_pagination(self, auth_headers):
        """
        Test: Verificar paginación por defecto (page=1, page_size=2000).
        
        Verifica que:
        - Con 230 registros y page_size=2000:
          - total_pages = 1
          - current_page = 1
          - has_next = false
          - has_previous = false
        - Se devuelven los 230 registros en la primera página
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre"},
            headers=auth_headers
        )
        
        data = response.json()
        pagination = data["data"]["pagination"]
        
        assert pagination["current_page"] == 1, \
            "La página actual debe ser 1"
        assert pagination["page_size"] == 2000, \
            "El tamaño de página por defecto debe ser 2000"
        assert pagination["total_pages"] == 1, \
            "Con 230 registros y page_size=2000 debe haber 1 página"
        assert pagination["has_next"] is False, \
            "No debe haber página siguiente"
        assert pagination["has_previous"] is False, \
            "No debe haber página anterior"
        
        records = data["data"]["records"]
        assert len(records) == 230, \
            "Debe devolver los 230 registros en la primera página"


class TestGetCardDataRecordStructure:
    """
    Tests para verificar la estructura de los registros.
    """
    
    def test_get_card_data_record_structure(self, auth_headers):
        """
        Test: Cada registro debe tener la estructura correcta.
        
        Verifica que cada record tiene:
        - operacion (string)
        - fecha_hora (string en formato YYYY-MM-DD HH:MM:SS)
        - tipo (string)
        - importe (number)
        - comision (number)
        - establecimiento (string)
        - source_file (string)
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre"},
            headers=auth_headers
        )
        
        data = response.json()
        records = data["data"]["records"]
        
        assert len(records) > 0, \
            "Debe haber al menos un registro para verificar"
        
        for record in records:
            # Verificar campos requeridos
            assert "operacion" in record, \
                "Cada record debe tener 'operacion'"
            assert "fecha_hora" in record, \
                "Cada record debe tener 'fecha_hora'"
            assert "tipo" in record, \
                "Cada record debe tener 'tipo'"
            assert "importe" in record, \
                "Cada record debe tener 'importe'"
            assert "comision" in record, \
                "Cada record debe tener 'comision'"
            assert "establecimiento" in record, \
                "Cada record debe tener 'establecimiento'"
            assert "source_file" in record, \
                "Cada record debe tener 'source_file'"
            
            # Verificar formato de fecha_hora (YYYY-MM-DD HH:MM:SS o similar)
            assert len(record["fecha_hora"]) >= 10, \
                "fecha_hora debe tener al menos formato de fecha YYYY-MM-DD"
            
            # Verificar tipos
            assert isinstance(record["operacion"], str), \
                "operacion debe ser string"
            assert isinstance(record["tipo"], str), \
                "tipo debe ser string"
            assert isinstance(record["importe"], (int, float)), \
                "importe debe ser numérico"
            assert isinstance(record["comision"], (int, float)), \
                "comision debe ser numérico"
            assert isinstance(record["establecimiento"], str), \
                "establecimiento debe ser string"
            assert isinstance(record["source_file"], str), \
                "source_file debe ser string"
    
    def test_get_card_data_includes_source_file(self, auth_headers):
        """
        Test: Todos los registros deben incluir source_file de archivos CSV.
        
        Verifica que:
        - Todos los records tienen source_file
        - source_file corresponde a archivos .csv
        - Para PRE, debe ser 'MOV22698582-110225104150.csv'
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre"},
            headers=auth_headers
        )
        
        data = response.json()
        records = data["data"]["records"]
        
        for record in records:
            source_file = record["source_file"]
            assert source_file.endswith(".csv"), \
                f"source_file debe ser CSV, es {source_file}"
            
            # En PRE solo hay un archivo CSV
            assert "MOV22698582" in source_file or "mov22698582" in source_file.lower(), \
                f"En PRE el source_file debe ser MOV22698582-110225104150.csv, es {source_file}"


class TestGetCardDataPagination:
    """
    Tests para verificar el comportamiento de paginación.
    """
    
    def test_get_card_data_small_page_size(self, auth_headers):
        """
        Test: Paginación con page_size pequeño.
        
        Verifica que:
        - Con page_size=10 y 230 registros:
          - total_pages = 23 (ceil(230/10))
          - Página 1 devuelve exactamente 10 registros
          - has_next = true
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre", "page_size": 10},
            headers=auth_headers
        )
        
        data = response.json()
        pagination = data["data"]["pagination"]
        
        assert pagination["page_size"] == 10, \
            "page_size debe ser 10"
        assert pagination["total_pages"] == 23, \
            "Con 230 registros y page_size=10 debe haber 23 páginas (ceil(230/10))"
        assert pagination["has_next"] is True, \
            "Debe haber página siguiente"
        
        records = data["data"]["records"]
        assert len(records) == 10, \
            "La página 1 debe devolver exactamente 10 registros"
    
    def test_get_card_data_last_page(self, auth_headers):
        """
        Test: Última página con registros restantes.
        
        Verifica que:
        - Página 23 con page_size=10 devuelve 10 registros (230/10 = 23 exacto)
        - has_next = false
        - has_previous = true
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre", "page": 23, "page_size": 10},
            headers=auth_headers
        )
        
        data = response.json()
        pagination = data["data"]["pagination"]
        
        assert pagination["current_page"] == 23, \
            "Debe estar en la página 23"
        assert pagination["has_next"] is False, \
            "No debe haber página siguiente (última página)"
        assert pagination["has_previous"] is True, \
            "Debe haber página anterior"
        
        records = data["data"]["records"]
        assert len(records) == 10, \
            "La última página debe devolver 10 registros (230 es múltiplo de 10)"
    
    def test_get_card_data_page_out_of_range(self, auth_headers):
        """
        Test: Solicitar una página fuera de rango devuelve error.
        
        Verifica que:
        - page=999 devuelve 400
        - El error indica página inválida
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre", "page": 999},
            headers=auth_headers
        )
        
        assert response.status_code == 400, \
            "Página fuera de rango debe devolver 400"
        
        data = response.json()
        assert data["error"]["code"] == "INVALID_PAGE", \
            "El código debe ser INVALID_PAGE"


class TestGetCardDataOrdering:
    """
    Tests para verificar el ordenamiento de registros.
    """
    
    def test_get_card_data_records_ordered_by_datetime(self, auth_headers):
        """
        Test: Los registros deben estar ordenados por fecha_hora ascendente.
        
        Verifica que:
        - Los registros están ordenados por el campo 'fecha_hora'
        - El ordenamiento es ascendente (más antiguo primero)
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pre"},
            headers=auth_headers
        )
        
        data = response.json()
        records = data["data"]["records"]
        
        # Verificar que hay suficientes registros para validar orden
        assert len(records) > 1, \
            "Debe haber al menos 2 registros para verificar orden"
        
        # Extraer fechas_hora
        fechas_hora = [record["fecha_hora"] for record in records]
        
        # Verificar que están ordenadas
        fechas_hora_ordenadas = sorted(fechas_hora)
        assert fechas_hora == fechas_hora_ordenadas, \
            "Los registros deben estar ordenados por fecha_hora ascendente"
        
        # Verificar que el primer registro es el más antiguo
        # Para el archivo CSV sabemos que va de 2024-10-16 a 2024-12-31
        assert records[0]["fecha_hora"].startswith("2024-10-16"), \
            f"El primer registro debe ser del 2024-10-16, es {records[0]['fecha_hora']}"


class TestGetCardDataEmptyEnvironment:
    """
    Tests para entornos sin datos.
    """
    
    def test_get_card_data_pro_empty(self, auth_headers):
        """
        Test: Entorno PRO sin datos devuelve respuesta vacía válida.
        
        Verifica que:
        - Devuelve 200 (no error)
        - records = []
        - total_records = 0
        - total_pages = 0
        """
        response = requests.get(
            CARD_DATA_ENDPOINT,
            params={"environment": "pro"},
            headers=auth_headers
        )
        
        assert response.status_code == 200, \
            "Entorno sin datos debe devolver 200"
        
        data = response.json()
        assert data["success"] is True, \
            "success debe ser true incluso sin datos"
        
        card_data = data["data"]
        assert card_data["environment"] == "pro", \
            "El entorno debe ser 'pro'"
        
        pagination = card_data["pagination"]
        assert pagination["total_records"] == 0, \
            "total_records debe ser 0"
        assert pagination["total_pages"] == 0, \
            "total_pages debe ser 0"
        
        records = card_data["records"]
        assert records == [], \
            "records debe ser un array vacío"
