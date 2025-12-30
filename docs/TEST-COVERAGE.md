# Configuración de Test Coverage con SonarCloud

Este proyecto está configurado para generar reportes de cobertura de código (test coverage) que se integran con SonarCloud.

## 🎯 Objetivo

Medir qué porcentaje del código fuente de los microservicios está siendo probado por los tests automatizados.

## 📊 Configuración

### Archivos de Configuración

- **`.coveragerc`**: Configuración de coverage.py
  - Define qué código se incluye/excluye del análisis
  - Configura formatos de reporte (XML, HTML, terminal)
  
- **`sonar-project.properties`**: Configuración de SonarCloud
  - `sonar.python.coverage.reportPaths=coverage.xml`
  - `sonar.sources=services` (solo código de microservicios)
  
- **`.github/workflows/sonarcloud.yml`**: CI/CD
  - Ejecuta tests con coverage en cada push/PR
  - Envía reportes a SonarCloud automáticamente

### Dependencias

```bash
pytest>=7.4.0
pytest-cov>=4.1.0
coverage>=7.10.6
```

## 🚀 Uso Local

### Ejecutar tests con coverage

```bash
# Usando el script incluido
./run-tests-with-coverage.sh

# O manualmente
pytest tests/ \
    --cov=services \
    --cov-config=.coveragerc \
    --cov-report=xml:coverage.xml \
    --cov-report=html:htmlcov \
    --cov-report=term-missing \
    -v
```

### Ver reportes

**Terminal**: El reporte se muestra automáticamente al ejecutar los tests

**HTML**: Abre `htmlcov/index.html` en tu navegador
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**SonarCloud**: Visita https://sonarcloud.io/project/overview?id=JoseMariaMorenoTerren_analisis-de-gastos

## 📈 Interpretación

### Qué se mide

- **Lines Coverage**: Porcentaje de líneas ejecutadas
- **Branch Coverage**: Porcentaje de ramas (if/else) probadas
- **Function Coverage**: Porcentaje de funciones llamadas

### Qué se excluye

- Archivos de tests (`tests/`)
- Código de terceros (`venv/`, `site-packages/`)
- Líneas de configuración estándar
- Código de depuración

## 🎯 Objetivos de Coverage

| Tipo | Mínimo | Objetivo |
|------|--------|----------|
| General | 70% | 80%+ |
| Crítico | 90% | 95%+ |

**Código crítico**: Autenticación, validación de datos, lógica de negocio

## 🔄 Integración CI/CD

Cada push a `main` o PR:
1. ✅ Ejecuta todos los tests
2. 📊 Genera reporte XML de coverage
3. ☁️ Envía reporte a SonarCloud
4. 📈 Actualiza métricas en dashboard

## 🛠️ Troubleshooting

### "No data was collected"

**Causa**: Los microservicios corren en procesos separados durante los tests de integración.

**Solución actual**: Los tests de integración no contribuyen a coverage, pero los tests unitarios sí.

**Mejora futura**: Implementar coverage para servicios en ejecución usando `coverage run`.

### Coverage muy bajo

**Verificar**:
1. ¿Los tests están en `tests/`?
2. ¿Los servicios están en `services/`?
3. ¿Se importan correctamente los módulos?

**Aumentar coverage**:
1. Añadir tests unitarios para funciones individuales
2. Probar casos edge y errores
3. Verificar todas las ramas (if/else)

## 📚 Referencias

- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [SonarCloud Python Coverage](https://docs.sonarcloud.io/enriching/test-coverage/python-test-coverage/)
