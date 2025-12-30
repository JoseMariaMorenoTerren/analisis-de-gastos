# Caso de Uso 01: Inicio de Sesión (Login)

## Descripción
Este caso de uso describe el proceso de autenticación de un usuario en el sistema a través de la API REST del microservicio de autenticación.

## Actores
- Usuario (cliente de la API)
- Microservicio de Autenticación

## Precondiciones
- El usuario debe estar previamente registrado en el sistema
- El microservicio de autenticación debe estar disponible y operativo
- El usuario debe tener credenciales válidas (email/usuario y contraseña)

## Flujo Principal

### 1. Solicitud de Autenticación
El cliente envía una petición POST al endpoint de login con las credenciales del usuario.

**Endpoint:** `POST /api/v1/auth/login`

**Estructura de la petición:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura"
}
```

### 2. Validación de Credenciales
El microservicio de autenticación:
- Valida que los campos requeridos estén presentes
- Verifica que el email tenga un formato válido
- Busca el usuario en la base de datos
- Compara la contraseña proporcionada con el hash almacenado

### 3. Generación de Token
Si las credenciales son válidas:
- El sistema genera un token JWT (JSON Web Token)
- El token incluye información del usuario (id, email, roles)
- Se establece un tiempo de expiración para el token

### 4. Respuesta Exitosa
El sistema devuelve una respuesta exitosa con el token de autenticación.

**Código HTTP:** `200 OK`

**Estructura de la respuesta:**
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "usuario@ejemplo.com",
      "name": "Nombre Usuario"
    }
  }
}
```

## Flujos Alternativos

### A1: Credenciales Inválidas
**Condición:** La contraseña no coincide con la almacenada

**Código HTTP:** `401 Unauthorized`

**Respuesta:**
```json
{
  "success": false,
  "message": "Credenciales inválidas",
  "error_code": "INVALID_CREDENTIALS"
}
```

### A2: Usuario No Encontrado
**Condición:** El email proporcionado no existe en el sistema

**Código HTTP:** `401 Unauthorized`

**Respuesta:**
```json
{
  "success": false,
  "message": "Credenciales inválidas",
  "error_code": "INVALID_CREDENTIALS"
}
```

*Nota: Por seguridad, se devuelve el mismo mensaje que en A1 para no revelar si el usuario existe o no*

### A3: Campos Faltantes
**Condición:** No se proporcionan email o contraseña

**Código HTTP:** `400 Bad Request`

**Respuesta:**
```json
{
  "success": false,
  "message": "Datos incompletos",
  "errors": {
    "email": ["El campo email es requerido"],
    "password": ["El campo password es requerido"]
  },
  "error_code": "VALIDATION_ERROR"
}
```

### A4: Formato de Email Inválido
**Condición:** El email no tiene un formato válido

**Código HTTP:** `400 Bad Request`

**Respuesta:**
```json
{
  "success": false,
  "message": "Datos inválidos",
  "errors": {
    "email": ["El email debe tener un formato válido"]
  },
  "error_code": "VALIDATION_ERROR"
}
```

### A5: Cuenta Bloqueada o Inactiva
**Condición:** La cuenta del usuario está bloqueada o desactivada

**Código HTTP:** `403 Forbidden`

**Respuesta:**
```json
{
  "success": false,
  "message": "Cuenta bloqueada o inactiva",
  "error_code": "ACCOUNT_DISABLED"
}
```

## Poscondiciones
- **Éxito:** El usuario recibe un token JWT válido que puede usar para autenticar futuras peticiones
- **Fallo:** El usuario recibe un mensaje de error descriptivo

## Requisitos No Funcionales

### Seguridad
- Las contraseñas nunca deben transmitirse o almacenarse en texto plano
- Se debe utilizar HTTPS para todas las comunicaciones
- Los tokens JWT deben firmarse con una clave secreta
- Implementar rate limiting para prevenir ataques de fuerza bruta

### Rendimiento
- El tiempo de respuesta debe ser inferior a 500ms en condiciones normales
- El servicio debe soportar al menos 100 peticiones concurrentes

### Disponibilidad
- El servicio debe tener una disponibilidad del 99.9%

## Consideraciones Técnicas

### Headers Requeridos
```
Content-Type: application/json
```

### Headers de Respuesta
```
Content-Type: application/json
```

### Validaciones
- Email: formato válido, longitud máxima 255 caracteres
- Password: mínimo 8 caracteres (en fase de login no se valida complejidad, solo autenticación)

## Diagrama de Flujo

```
┌─────────┐                 ┌──────────────────┐
│ Cliente │                 │ Microservicio    │
│         │                 │ Autenticación    │
└────┬────┘                 └────────┬─────────┘
     │                               │
     │ POST /api/v1/auth/login       │
     │ {email, password}             │
     ├──────────────────────────────>│
     │                               │
     │                               ├─ Validar formato
     │                               │
     │                               ├─ Buscar usuario
     │                               │
     │                               ├─ Verificar password
     │                               │
     │                               ├─ Generar JWT
     │                               │
     │ 200 OK                        │
     │ {token, user}                 │
     │<──────────────────────────────┤
     │                               │
```

## Notas Adicionales
- Este caso de uso se centra en la autenticación básica con email y contraseña
- Futuros casos de uso podrían incluir: registro, recuperación de contraseña, autenticación de dos factores, refresh token, etc.
- El token JWT será necesario para acceder a los endpoints protegidos de los otros microservicios (recopilación y manipulación de datos)
