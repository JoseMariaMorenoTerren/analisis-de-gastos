# Tests Unitarios

Este directorio contiene tests unitarios que importan directamente
las funciones y clases del código fuente para generar métricas de
cobertura (coverage).

## Diferencia con tests de integración

- **Tests de integración** (`../test_*.py`): Prueban endpoints HTTP completos
- **Tests unitarios** (`./test_*_unit.py`): Prueban funciones individuales

## Ejecución

```bash
# Ejecutar solo tests unitarios
pytest tests/unit/ -v

# Con coverage
pytest tests/unit/ --cov=services --cov-report=term-missing
```
