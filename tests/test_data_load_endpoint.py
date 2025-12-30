"""
Tests de integración para los endpoints de carga de datos del microservicio de recopilación.

Este módulo contiene las pruebas de integración para validar el comportamiento
del endpoint de carga de datos según el caso de uso 03: Carga de Datos.
"""

import pytest
import requests
import os
from typing import Dict, Any


# Configuración del microservicio de recopilación de datos
DATA_COLLECTION_SERVICE_URL = "http://localhost:8002"
LOAD_PRE_ENDPOINT = f"{DATA_COLLECTION_SERVICE_URL}/api/v1/data/load/pre"
LOAD_PRO_ENDPOINT = f"{DATA_COLLECTION_SERVICE_URL}/api/v1/data/load/pro"


class TestDataLoadEndpoint:
    """Tests para el endpoint de carga de datos desde PRE."""
    
    @pytest.fixture
    def valid_token(self) -> str:
        """Token JWT válido para testing."""
        # En una implementación real, este token vendría del servicio de autenticación
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token.signature"
    
    @pytest.fixture
    def auth_headers(self, valid_token: str) -> Dict[str, str]:
        """Headers con autenticación para las peticiones."""
        return {
            "Authorization": f"Bearer {valid_token}",
            "Content-Type": "application/json"
        }
    
    def test_load_pre_requires_authentication(self):
        """
        Test: El endpoint debe requerir autenticación.
        
        Verifica que:
        - Sin token devuelve 401 Unauthorized
        """
        response = requests.post(
            LOAD_PRE_ENDPOINT,
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401, \
            f"Se esperaba código 401, se obtuvo {response.status_code}"
    
    def test_load_pre_successful(self, auth_headers):
        """
        Test: Carga exitosa de archivos desde PRE.
        
        Verifica que:
        - El código de respuesta sea 200 OK
        - La respuesta contenga la lista de archivos cargados
        - Se detecten archivos CSV y XLSX
        - Cada archivo tenga los metadatos correctos
        """
        response = requests.post(
            LOAD_PRE_ENDPOINT,
            json={},
            headers=auth_headers
        )
        
        assert response.status_code == 200, \
            f"Se esperaba código 200, se obtuvo {response.status_code}"
        
        data = response.json()
        
        # Verificar estructura de respuesta
        assert data["success"] is True, "El campo 'success' debe ser True"
        assert "message" in data, "La respuesta debe contener 'message'"
        assert "data" in data, "La respuesta debe contener 'data'"
        
        # Verificar datos de la carga
        load_data = data["data"]
        assert load_data["environment"] == "pre", \
            "El entorno debe ser 'pre'"
        assert "total_files" in load_data, \
            "Debe incluir 'total_files'"
        assert "total_records" in load_data, \
            "Debe incluir 'total_records'"
        assert "files" in load_data, \
            "Debe incluir el array 'files'"
        assert "loaded_at" in load_data, \
            "Debe incluir timestamp 'loaded_at'"
    
    def test_load_pre_detects_multiple_files(self, auth_headers):
        """
        Test: Debe detectar múltiples archivos (CSV y XLS).
        
        Verifica que:
        - Se detectan exactamente 2 archivos
        - Se detecta 1 archivo CSV
        - Se detecta 1 archivo XLS
        """
        response = requests.post(
            LOAD_PRE_ENDPOINT,
            json={},
            headers=auth_headers
        )
        
        data = response.json()
        files = data["data"]["files"]
        
        assert len(files) == 2, \
            f"Se esperaban exactamente 2 archivos, se encontraron {len(files)}"
        
        # Verificar que hay archivos CSV y XLS
        formats = [f["format"] for f in files]
        assert "csv" in formats, "Debe haber al menos un archivo CSV"
        assert any(fmt in ["xls", "xlsx"] for fmt in formats), "Debe haber al menos un archivo XLS o XLSX"
    
    def test_load_pre_file_metadata(self, auth_headers):
        """
        Test: Cada archivo debe tener los metadatos correctos.
        
        Verifica que:
        - Cada archivo tiene filename, format, records, fecha_inicio, fecha_fin
        - El número de registros es mayor que 0
        - Las fechas están en formato correcto
        - La fecha_fin es mayor o igual a fecha_inicio
        """
        response = requests.post(
            LOAD_PRE_ENDPOINT,
            json={},
            headers=auth_headers
        )
        
        data = response.json()
        files = data["data"]["files"]
        
        for file_info in files:
            # Verificar campos requeridos
            assert "filename" in file_info, "Debe tener 'filename'"
            assert "format" in file_info, "Debe tener 'format'"
            assert "records" in file_info, "Debe tener 'records'"
            assert "fecha_inicio" in file_info, "Debe tener 'fecha_inicio'"
            assert "fecha_fin" in file_info, "Debe tener 'fecha_fin'"
            
            # Verificar tipos y valores
            assert isinstance(file_info["records"], int), \
                "'records' debe ser un número entero"
            assert file_info["records"] > 0, \
                f"El archivo {file_info['filename']} debe tener registros"
            
            # Verificar formato de fechas (YYYY-MM-DD)
            assert len(file_info["fecha_inicio"]) == 10, \
                "fecha_inicio debe tener formato YYYY-MM-DD"
            assert len(file_info["fecha_fin"]) == 10, \
                "fecha_fin debe tener formato YYYY-MM-DD"
            
            # Verificar que fecha_fin >= fecha_inicio
            assert file_info["fecha_fin"] >= file_info["fecha_inicio"], \
                f"fecha_fin debe ser >= fecha_inicio en {file_info['filename']}"
    
    def test_load_pre_csv_file_details(self, auth_headers):
        """
        Test: Verificar detalles específicos del archivo CSV.
        
        Verifica que:
        - El archivo CSV tiene el nombre esperado
        - Tiene 231 registros (230 + header)
        - Las fechas van de octubre a diciembre 2024
        """
        response = requests.post(
            LOAD_PRE_ENDPOINT,
            json={},
            headers=auth_headers
        )
        
        data = response.json()
        files = data["data"]["files"]
        
        # Buscar el archivo CSV
        csv_files = [f for f in files if f["format"] == "csv"]
        assert len(csv_files) > 0, "Debe haber al menos un archivo CSV"
        
        csv_file = csv_files[0]
        assert "MOV22698582" in csv_file["filename"] or "mov22698582" in csv_file["filename"].lower(), \
            f"El archivo CSV debe ser MOV22698582-110225104150.csv, se encontró {csv_file['filename']}"
        assert csv_file["records"] == 230, \
            f"El CSV debe tener 230 registros (sin contar header), tiene {csv_file['records']}"
        assert csv_file["fecha_inicio"] == "2024-10-16", \
            f"La fecha de inicio del CSV debe ser 2024-10-16, es {csv_file['fecha_inicio']}"
        assert csv_file["fecha_fin"] == "2024-12-31", \
            f"La fecha de fin del CSV debe ser 2024-12-31, es {csv_file['fecha_fin']}"
    
    def test_load_pre_xlsx_file_details(self, auth_headers):
        """
        Test: Verificar detalles específicos del archivo XLS.
        
        Verifica que:
        - El archivo XLS tiene el nombre esperado
        - Tiene 43 registros
        - Las fechas son de enero 2025
        """
        response = requests.post(
            LOAD_PRE_ENDPOINT,
            json={},
            headers=auth_headers
        )
        
        data = response.json()
        files = data["data"]["files"]
        
        # Buscar el archivo XLS
        xls_files = [f for f in files if f["format"] in ["xls", "xlsx"]]
        assert len(xls_files) > 0, "Debe haber al menos un archivo XLS"
        
        xls_file = xls_files[0]
        assert "excelFile" in xls_file["filename"] or "excelfile" in xls_file["filename"].lower(), \
            f"El archivo XLS debe ser excelFile_1739266641274.xls, se encontró {xls_file['filename']}"
        assert xls_file["records"] == 43, \
            f"El XLS debe tener 43 registros, tiene {xls_file['records']}"
        assert xls_file["fecha_inicio"] == "2025-01-01", \
            f"La fecha de inicio del XLS debe ser 2025-01-01, es {xls_file['fecha_inicio']}"
        assert xls_file["fecha_fin"] == "2025-01-31", \
            f"La fecha de fin del XLS debe ser 2025-01-31, es {xls_file['fecha_fin']}"
    
    def test_load_pre_total_records(self, auth_headers):
        """
        Test: El total de registros debe ser la suma de todos los archivos.
        
        Verifica que:
        - total_records = suma de records de todos los archivos
        - Para nuestros archivos de prueba: 230 (CSV) + 43 (XLS) = 273
        """
        response = requests.post(
            LOAD_PRE_ENDPOINT,
            json={},
            headers=auth_headers
        )
        
        data = response.json()
        load_data = data["data"]
        
        # Calcular suma de registros
        sum_records = sum(f["records"] for f in load_data["files"])
        
        assert load_data["total_records"] == sum_records, \
            f"total_records ({load_data['total_records']}) debe ser igual a la suma ({sum_records})"
        
        # Verificar el valor esperado para nuestros archivos de prueba
        assert load_data["total_records"] == 273, \
            f"Se esperaban 273 registros totales (230 CSV + 43 XLS), se obtuvieron {load_data['total_records']}"
    
    def test_load_pre_total_files(self, auth_headers):
        """
        Test: El total de archivos debe coincidir con la cantidad en el array.
        
        Verifica que:
        - total_files = len(files)
        - Para nuestros datos de prueba: 2 archivos
        """
        response = requests.post(
            LOAD_PRE_ENDPOINT,
            json={},
            headers=auth_headers
        )
        
        data = response.json()
        load_data = data["data"]
        
        assert load_data["total_files"] == len(load_data["files"]), \
            "total_files debe coincidir con la longitud del array files"
        
        assert load_data["total_files"] == 2, \
            f"Se esperaban 2 archivos, se obtuvieron {load_data['total_files']}"
    
    def test_load_pre_content_type(self, auth_headers):
        """
        Test: El Content-Type de la respuesta debe ser application/json.
        
        Verifica que:
        - El header Content-Type es application/json
        """
        response = requests.post(
            LOAD_PRE_ENDPOINT,
            json={},
            headers=auth_headers
        )
        
        assert "application/json" in response.headers.get("Content-Type", ""), \
            "El Content-Type debe ser application/json"
    
    def test_load_pre_idempotent(self, auth_headers):
        """
        Test: Múltiples llamadas deben devolver los mismos datos.
        
        Verifica que:
        - Llamar al endpoint múltiples veces devuelve resultados consistentes
        """
        response1 = requests.post(LOAD_PRE_ENDPOINT, json={}, headers=auth_headers)
        response2 = requests.post(LOAD_PRE_ENDPOINT, json={}, headers=auth_headers)
        
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["data"]["total_files"] == data2["data"]["total_files"], \
            "El número de archivos debe ser consistente"
        assert data1["data"]["total_records"] == data2["data"]["total_records"], \
            "El número de registros debe ser consistente"


class TestDataLoadProEndpoint:
    """Tests para el endpoint de carga de datos desde PRO."""
    
    @pytest.fixture
    def auth_headers(self) -> Dict[str, str]:
        """Headers con autenticación para las peticiones."""
        return {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token.signature",
            "Content-Type": "application/json"
        }
    
    def test_load_pro_requires_authentication(self):
        """
        Test: El endpoint PRO también debe requerir autenticación.
        
        Verifica que:
        - Sin token devuelve 401 Unauthorized
        """
        response = requests.post(
            LOAD_PRO_ENDPOINT,
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401, \
            f"Se esperaba código 401, se obtuvo {response.status_code}"
    
    def test_load_pro_environment_field(self, auth_headers):
        """
        Test: El endpoint PRO debe indicar environment='pro'.
        
        Verifica que:
        - El campo environment es 'pro'
        - La estructura es similar a PRE pero con datos de datos-pro/
        """
        response = requests.post(
            LOAD_PRO_ENDPOINT,
            json={},
            headers=auth_headers
        )
        
        # Puede devolver 200 (si hay archivos) o 404 (si no hay archivos en PRO)
        if response.status_code == 200:
            data = response.json()
            assert data["data"]["environment"] == "pro", \
                "El entorno debe ser 'pro'"
        elif response.status_code == 404:
            # Es aceptable si no hay archivos en PRO
            data = response.json()
            assert data["success"] is False, \
                "success debe ser False cuando no hay archivos"
        else:
            pytest.fail(f"Código inesperado: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
