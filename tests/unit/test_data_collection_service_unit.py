"""
Tests unitarios para el microservicio de recopilación de datos.

Este módulo contiene las pruebas unitarias para las funciones del servicio
de recopilación de datos, probando cada función de forma aislada.
"""

import pytest
import pandas as pd
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import jwt

# Importar el módulo a testear
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "data-collection-service"))

from app.main import (
    save_state,
    load_state,
    verify_token,
    detect_date_column,
    parse_date_column,
    load_file,
    ESTADO,
    STATE_FILE,
    JWT_SECRET_KEY,
    JWT_ALGORITHM
)


class TestSaveState:
    """Tests para la función save_state()"""
    
    def test_save_state_creates_file(self, tmp_path):
        """Test: save_state debe crear el archivo JSON"""
        # Preparar
        import app.main as main_module
        original_state_file = main_module.STATE_FILE
        test_file = tmp_path / "test_estado.json"
        main_module.STATE_FILE = test_file
        
        # Ejecutar
        save_state()
        
        # Verificar
        assert test_file.exists(), "El archivo debe existir después de save_state()"
        
        # Restaurar
        main_module.STATE_FILE = original_state_file
    
    def test_save_state_saves_correct_format(self, tmp_path):
        """Test: save_state debe guardar el estado en formato JSON válido"""
        # Preparar
        import app.main as main_module
        original_state_file = main_module.STATE_FILE
        test_file = tmp_path / "test_estado.json"
        main_module.STATE_FILE = test_file
        
        # Ejecutar
        save_state()
        
        # Verificar
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "environments" in data, "Debe contener 'environments'"
        assert "data" in data, "Debe contener 'data'"
        assert "pre" in data["environments"], "Debe tener entorno 'pre'"
        assert "pro" in data["environments"], "Debe tener entorno 'pro'"
        
        # Restaurar
        main_module.STATE_FILE = original_state_file
    
    def test_save_state_creates_directory_if_not_exists(self, tmp_path):
        """Test: save_state debe crear el directorio si no existe"""
        # Preparar
        import app.main as main_module
        original_state_file = main_module.STATE_FILE
        test_file = tmp_path / "nested" / "dir" / "test_estado.json"
        main_module.STATE_FILE = test_file
        
        # Verificar que el directorio no existe
        assert not test_file.parent.exists()
        
        # Ejecutar
        save_state()
        
        # Verificar
        assert test_file.parent.exists(), "El directorio debe existir"
        assert test_file.exists(), "El archivo debe existir"
        
        # Restaurar
        main_module.STATE_FILE = original_state_file


class TestLoadState:
    """Tests para la función load_state()"""
    
    def test_load_state_loads_existing_file(self, tmp_path):
        """Test: load_state debe cargar el estado desde un archivo existente"""
        # Preparar
        import app.main as main_module
        original_state_file = main_module.STATE_FILE
        test_file = tmp_path / "test_estado.json"
        
        test_data = {
            "environments": {
                "pre": {
                    "loaded": True,
                    "loaded_at": "2025-12-30T10:00:00",
                    "files": [],
                    "total_records": 100,
                    "total_files": 2
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
                "pre": [{"test": "data"}],
                "pro": []
            }
        }
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        main_module.STATE_FILE = test_file
        
        # Ejecutar
        load_state()
        
        # Verificar
        assert main_module.ESTADO["environments"]["pre"]["total_records"] == 100
        assert main_module.ESTADO["environments"]["pre"]["loaded"] is True
        
        # Restaurar
        main_module.STATE_FILE = original_state_file
    
    def test_load_state_handles_missing_file(self, tmp_path):
        """Test: load_state debe manejar correctamente cuando el archivo no existe"""
        # Preparar
        import app.main as main_module
        original_state_file = main_module.STATE_FILE
        test_file = tmp_path / "nonexistent.json"
        main_module.STATE_FILE = test_file
        
        # Ejecutar (no debe lanzar excepción)
        load_state()
        
        # Verificar que el estado inicial se mantiene
        assert "environments" in main_module.ESTADO
        
        # Restaurar
        main_module.STATE_FILE = original_state_file


class TestVerifyToken:
    """Tests para la función verify_token()"""
    
    def test_verify_token_with_valid_token(self):
        """Test: verify_token debe aceptar un token válido"""
        # Preparar - crear un token válido
        from datetime import datetime, timedelta, timezone
        payload = {
            "sub": "test@example.com",
            "user_id": "123",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        authorization = f"Bearer {token}"
        
        # Ejecutar
        result = verify_token(authorization)
        
        # Verificar
        assert result["sub"] == "test@example.com"
        assert result["user_id"] == "123"
    
    def test_verify_token_rejects_missing_token(self):
        """Test: verify_token debe rechazar cuando no hay token"""
        from fastapi import HTTPException
        
        # Ejecutar y verificar
        with pytest.raises(HTTPException) as exc_info:
            verify_token(None)
        
        assert exc_info.value.status_code == 401
        assert "MISSING_TOKEN" in str(exc_info.value.detail)
    
    def test_verify_token_rejects_invalid_format(self):
        """Test: verify_token debe rechazar formato inválido"""
        from fastapi import HTTPException
        
        # Ejecutar y verificar
        with pytest.raises(HTTPException) as exc_info:
            verify_token("InvalidFormat")
        
        assert exc_info.value.status_code == 401
        assert "INVALID_TOKEN_FORMAT" in str(exc_info.value.detail)
    
    def test_verify_token_rejects_expired_token(self):
        """Test: verify_token debe rechazar token expirado"""
        from fastapi import HTTPException
        from datetime import datetime, timedelta, timezone
        
        # Preparar - crear un token expirado
        payload = {
            "sub": "test@example.com",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)  # Expirado
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        authorization = f"Bearer {token}"
        
        # Ejecutar y verificar
        with pytest.raises(HTTPException) as exc_info:
            verify_token(authorization)
        
        assert exc_info.value.status_code == 401
        assert "INVALID_TOKEN" in str(exc_info.value.detail)
    
    def test_verify_token_rejects_invalid_signature(self):
        """Test: verify_token debe rechazar token con firma inválida"""
        from fastapi import HTTPException
        from datetime import datetime, timedelta, timezone
        
        # Preparar - crear un token con clave incorrecta
        payload = {
            "sub": "test@example.com",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, "wrong-secret-key", algorithm=JWT_ALGORITHM)
        authorization = f"Bearer {token}"
        
        # Ejecutar y verificar
        with pytest.raises(HTTPException) as exc_info:
            verify_token(authorization)
        
        assert exc_info.value.status_code == 401


class TestDetectDateColumn:
    """Tests para la función detect_date_column()"""
    
    def test_detect_date_column_exact_match(self):
        """Test: debe detectar columna con nombre exacto 'fecha'"""
        # Preparar
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'fecha': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'amount': [100, 200, 300]
        })
        
        # Ejecutar
        result = detect_date_column(df)
        
        # Verificar
        assert result == 'fecha'
    
    def test_detect_date_column_fecha_y_hora(self):
        """Test: debe detectar 'Fecha y hora'"""
        # Preparar
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'Fecha y hora': ['2024-01-01 10:00', '2024-01-02 11:00', '2024-01-03 12:00'],
            'amount': [100, 200, 300]
        })
        
        # Ejecutar
        result = detect_date_column(df)
        
        # Verificar
        assert result == 'Fecha y hora'
    
    def test_detect_date_column_partial_match(self):
        """Test: debe detectar columna con 'fecha' en el nombre"""
        # Preparar
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'fecha_creacion': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'amount': [100, 200, 300]
        })
        
        # Ejecutar
        result = detect_date_column(df)
        
        # Verificar
        assert result == 'fecha_creacion'
    
    def test_detect_date_column_case_insensitive(self):
        """Test: debe ser case-insensitive en búsqueda parcial"""
        # Preparar
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'FECHA_REGISTRO': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'amount': [100, 200, 300]
        })
        
        # Ejecutar
        result = detect_date_column(df)
        
        # Verificar
        assert result == 'FECHA_REGISTRO'
    
    def test_detect_date_column_no_date_column(self):
        """Test: debe retornar None si no hay columna de fecha"""
        # Preparar
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'amount': [100, 200, 300],
            'description': ['A', 'B', 'C']
        })
        
        # Ejecutar
        result = detect_date_column(df)
        
        # Verificar
        assert result is None


class TestParseDateColumn:
    """Tests para la función parse_date_column()"""
    
    def test_parse_date_column_converts_to_datetime(self):
        """Test: debe convertir columna a datetime"""
        # Preparar
        df = pd.DataFrame({
            'fecha': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        
        # Ejecutar
        result = parse_date_column(df, 'fecha')
        
        # Verificar
        assert pd.api.types.is_datetime64_any_dtype(result['fecha'])
    
    def test_parse_date_column_handles_dd_mm_yyyy(self):
        """Test: debe manejar formato DD/MM/YYYY con dayfirst=True"""
        # Preparar
        df = pd.DataFrame({
            'fecha': ['15/01/2024', '20/02/2024', '25/03/2024']
        })
        
        # Ejecutar
        result = parse_date_column(df, 'fecha')
        
        # Verificar
        assert pd.api.types.is_datetime64_any_dtype(result['fecha'])
        # Verificar que el día 15 se interpretó correctamente (no como mes)
        assert result['fecha'].iloc[0].day == 15
        assert result['fecha'].iloc[0].month == 1
    
    def test_parse_date_column_handles_invalid_dates(self):
        """Test: debe manejar fechas inválidas sin error (coerce)"""
        # Preparar
        df = pd.DataFrame({
            'fecha': ['2024-01-01', 'invalid-date', '2024-01-03']
        })
        
        # Ejecutar
        result = parse_date_column(df, 'fecha')
        
        # Verificar
        assert pd.isna(result['fecha'].iloc[1])  # La fecha inválida debe ser NaT
        assert not pd.isna(result['fecha'].iloc[0])
        assert not pd.isna(result['fecha'].iloc[2])
    
    def test_parse_date_column_handles_exception(self):
        """Test: debe manejar excepciones y retornar el DataFrame original"""
        # Preparar
        df = pd.DataFrame({
            'fecha': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        
        # Ejecutar con columna inexistente
        result = parse_date_column(df, 'nonexistent_column')
        
        # Verificar que retorna el DataFrame original
        assert 'fecha' in result.columns


class TestLoadFile:
    """Tests para la función load_file()"""
    
    def test_load_file_csv_with_comma_delimiter(self, tmp_path):
        """Test: debe cargar archivo CSV con comas"""
        # Preparar
        csv_file = tmp_path / "test.csv"
        csv_content = """fecha,amount,description
2024-01-01,100,Test 1
2024-01-02,200,Test 2
2024-01-03,300,Test 3"""
        csv_file.write_text(csv_content)
        
        # Ejecutar
        df, file_info = load_file(csv_file)
        
        # Verificar
        assert len(df) == 3
        assert file_info['format'] == 'csv'
        assert file_info['records'] == 3
        assert file_info['filename'] == 'test.csv'
        assert 'size_bytes' in file_info
    
    def test_load_file_csv_with_semicolon_delimiter(self, tmp_path):
        """Test: debe detectar y cargar CSV con punto y coma"""
        # Preparar
        csv_file = tmp_path / "test.csv"
        csv_content = """fecha;amount;description
2024-01-01;100;Test 1
2024-01-02;200;Test 2"""
        csv_file.write_text(csv_content)
        
        # Ejecutar
        df, file_info = load_file(csv_file)
        
        # Verificar
        assert len(df) == 2
        assert 'fecha' in df.columns or 'amount' in df.columns
    
    def test_load_file_extracts_date_range(self, tmp_path):
        """Test: debe extraer rango de fechas"""
        # Preparar
        csv_file = tmp_path / "test.csv"
        csv_content = """fecha,amount
2024-01-15,100
2024-01-20,200
2024-01-25,300"""
        csv_file.write_text(csv_content)
        
        # Ejecutar
        df, file_info = load_file(csv_file)
        
        # Verificar
        assert file_info['fecha_inicio'] == '2024-01-15'
        assert file_info['fecha_fin'] == '2024-01-25'
    
    def test_load_file_handles_file_without_dates(self, tmp_path):
        """Test: debe manejar archivos sin columna de fecha"""
        # Preparar
        csv_file = tmp_path / "test.csv"
        csv_content = """id,amount,description
1,100,Test 1
2,200,Test 2"""
        csv_file.write_text(csv_content)
        
        # Ejecutar
        df, file_info = load_file(csv_file)
        
        # Verificar
        assert file_info['fecha_inicio'] is None
        assert file_info['fecha_fin'] is None
    
    def test_load_file_unsupported_format(self, tmp_path):
        """Test: debe rechazar formatos no soportados"""
        # Preparar
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("test content")
        
        # Ejecutar y verificar
        with pytest.raises(ValueError) as exc_info:
            load_file(txt_file)
        
        assert "Formato no soportado" in str(exc_info.value)


class TestIntegration:
    """Tests de integración entre funciones"""
    
    def test_save_and_load_state_round_trip(self, tmp_path):
        """Test: guardar y cargar estado debe ser consistente"""
        # Preparar
        import app.main as main_module
        original_state_file = main_module.STATE_FILE
        original_estado = main_module.ESTADO.copy()
        test_file = tmp_path / "test_estado.json"
        main_module.STATE_FILE = test_file
        
        # Modificar estado
        main_module.ESTADO["environments"]["pre"]["total_records"] = 999
        main_module.ESTADO["environments"]["pre"]["loaded"] = True
        
        # Guardar
        save_state()
        
        # Modificar estado en memoria
        main_module.ESTADO["environments"]["pre"]["total_records"] = 0
        
        # Cargar
        load_state()
        
        # Verificar que se recuperó el estado guardado
        assert main_module.ESTADO["environments"]["pre"]["total_records"] == 999
        assert main_module.ESTADO["environments"]["pre"]["loaded"] is True
        
        # Restaurar
        main_module.STATE_FILE = original_state_file
        main_module.ESTADO = original_estado


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
