# GitFlow - Análisis de Gastos

Este proyecto utiliza el modelo de ramificación **GitFlow** para gestionar el desarrollo.

## Ramas Principales

### `main`
- **Propósito**: Código en producción
- **Protección**: Solo acepta merges desde `release/*` o `hotfix/*`
- **Tags**: Todas las versiones de producción se tagean aquí (ej: `v1.0.0.0`)

### `develop`
- **Propósito**: Rama de integración para desarrollo
- **Protección**: Acepta merges desde `feature/*`
- **Estado**: Siempre debe estar en estado deployable

## Ramas de Soporte

### `feature/*`
- **Propósito**: Desarrollo de nuevas funcionalidades
- **Origen**: Ramifica desde `develop`
- **Destino**: Merge a `develop`
- **Nomenclatura**: `feature/nombre-descriptivo`
- **Ejemplo**: 
  ```bash
  git checkout develop
  git checkout -b feature/login-endpoint
  # ... desarrollo ...
  git checkout develop
  git merge --no-ff feature/login-endpoint
  git branch -d feature/login-endpoint
  ```

### `release/*`
- **Propósito**: Preparación de una nueva versión de producción
- **Origen**: Ramifica desde `develop`
- **Destino**: Merge a `main` y `develop`
- **Nomenclatura**: `release/v1.x.x.x`
- **Ejemplo**:
  ```bash
  git checkout develop
  git checkout -b release/v1.1.0.0
  # ... ajustes finales y testing ...
  git checkout main
  git merge --no-ff release/v1.1.0.0
  git tag -a v1.1.0.0
  git checkout develop
  git merge --no-ff release/v1.1.0.0
  git branch -d release/v1.1.0.0
  ```

### `hotfix/*`
- **Propósito**: Corrección urgente en producción
- **Origen**: Ramifica desde `main`
- **Destino**: Merge a `main` y `develop`
- **Nomenclatura**: `hotfix/descripcion-bug`
- **Ejemplo**:
  ```bash
  git checkout main
  git checkout -b hotfix/auth-token-validation
  # ... corrección ...
  git checkout main
  git merge --no-ff hotfix/auth-token-validation
  git tag -a v1.0.0.1
  git checkout develop
  git merge --no-ff hotfix/auth-token-validation
  git branch -d hotfix/auth-token-validation
  ```

## Esquema de Versionado

Seguimos el esquema **Semantic Versioning** adaptado:

```
v[MAJOR].[MINOR].[PATCH].[BUILD]
```

- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nueva funcionalidad compatible con versiones anteriores
- **PATCH**: Corrección de bugs compatible
- **BUILD**: Número de build incremental

**Ejemplos**:
- `v1.0.0.0` - Release inicial
- `v1.1.0.0` - Nueva funcionalidad (ej: implementar login)
- `v1.1.1.0` - Bug fix
- `v2.0.0.0` - Breaking change en la API

## Versión Actual

**v1.0.0.0** - Estructura base de microservicios
- ✅ 3 microservicios implementados
- ✅ Health check endpoints
- ✅ 21 tests de integración pasando
- ✅ Documentación OpenAPI completa
- ✅ SonarCloud configurado

## Workflow de Desarrollo

### Para nuevas funcionalidades:

1. **Crear feature branch desde develop**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/mi-funcionalidad
   ```

2. **Desarrollar con TDD**:
   - Escribir tests primero
   - Implementar código
   - Commit frecuentes con mensajes descriptivos

3. **Merge a develop**:
   ```bash
   git checkout develop
   git merge --no-ff feature/mi-funcionalidad
   git push origin develop
   git branch -d feature/mi-funcionalidad
   ```

### Para preparar un release:

1. **Crear release branch**:
   ```bash
   git checkout develop
   git checkout -b release/v1.1.0.0
   ```

2. **Ajustes finales**:
   - Actualizar versión en archivos
   - Ejecutar tests completos
   - Actualizar CHANGELOG

3. **Merge a main y develop**:
   ```bash
   git checkout main
   git merge --no-ff release/v1.1.0.0
   git tag -a v1.1.0.0 -m "Release v1.1.0.0"
   git push origin main --tags
   
   git checkout develop
   git merge --no-ff release/v1.1.0.0
   git push origin develop
   git branch -d release/v1.1.0.0
   ```

### Para hotfixes urgentes:

1. **Crear hotfix branch desde main**:
   ```bash
   git checkout main
   git checkout -b hotfix/descripcion-bug
   ```

2. **Corregir y probar**:
   - Implementar fix
   - Ejecutar tests
   - Verificar solución

3. **Merge a main y develop**:
   ```bash
   git checkout main
   git merge --no-ff hotfix/descripcion-bug
   git tag -a v1.0.0.1 -m "Hotfix: descripcion"
   git push origin main --tags
   
   git checkout develop
   git merge --no-ff hotfix/descripcion-bug
   git push origin develop
   git branch -d hotfix/descripcion-bug
   ```

## Reglas de Commits

- Usar mensajes descriptivos en presente imperativo
- Formato: `<tipo>: <descripción>`
- Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

**Ejemplos**:
```
feat: implementar endpoint de login con JWT
fix: corregir validación de tokens expirados
docs: actualizar README con instrucciones de deployment
test: agregar tests para paginación de datos
```

## Protección de Ramas

En GitHub, configurar:
- **main**: Requiere PR, 1 aprobación, tests pasando
- **develop**: Requiere PR, tests pasando
