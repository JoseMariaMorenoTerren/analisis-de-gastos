#!/bin/bash
# Script para ejecutar tests con coverage

# Determinar el ejecutable de pytest
if [ -f ".venv/bin/pytest" ]; then
    PYTEST=".venv/bin/pytest"
elif command -v pytest &> /dev/null; then
    PYTEST="pytest"
else
    echo "❌ Error: pytest no encontrado. Instala las dependencias con:"
    echo "   pip install -r requirements-test.txt"
    exit 1
fi

echo "🧪 Ejecutando tests con coverage..."

# Ejecutar todos los tests con coverage
$PYTEST tests/ \
    --cov=services \
    --cov-config=.coveragerc \
    --cov-report=xml:coverage.xml \
    --cov-report=html:htmlcov \
    --cov-report=term-missing \
    -v

EXIT_CODE=$?

echo ""
echo "📊 Reportes generados:"
echo "  - XML: coverage.xml (para SonarCloud)"
echo "  - HTML: htmlcov/index.html (para visualización local)"
echo ""

if [ -f coverage.xml ]; then
    echo "✅ Reporte XML generado correctamente"
else
    echo "❌ Error: No se generó el reporte XML"
fi

exit $EXIT_CODE
