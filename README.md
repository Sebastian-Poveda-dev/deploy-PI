# Clinica Juridica - Sistema de Gestion de Casos

Aplicacion web para la gestion de casos de un consultorio juridico universitario. El sistema permite administrar usuarios, roles, casos, documentos asociados, trazabilidad de actividades y notificaciones relacionadas con vencimientos de documentos.

## Descripcion general

La solucion esta construida con una arquitectura cliente-servidor dividida en dos aplicaciones principales:

- `backend/`: API y logica de negocio construidas con Django y Django REST Framework.
- `frontend/`: interfaz web construida con React y Vite.

La aplicacion maneja autenticacion por sesion, control de acceso por roles, persistencia en SQLite para desarrollo y almacenamiento local de archivos en `backend/media/`.

## Funcionalidades principales

- Registro y autenticacion de usuarios.
- Gestion de roles del sistema: `admin`, `advisor`, `professor`, `student`, `beneficiary`.
- Creacion, consulta y actualizacion de casos.
- Aprobacion de casos y rechazo de asignaciones segun reglas de negocio.
- Registro de documentos por caso, descarga de documentos y trazabilidad en bitacora.
- Consulta y registro de logs asociados a cada caso.
- Notificaciones de vencimiento de documentos para el estudiante asignado y el `advisor` asignado al caso.

## Arquitectura actual

### Backend

El backend expone endpoints HTTP organizados por dominios funcionales:

- `users/`: autenticacion, perfil del usuario, beneficiarios, profesores y administracion de usuarios.
- `cases/`: creacion, consulta, actualizacion, aprobacion, rechazo de asignacion y logs de casos.
- `documents/`: descarga de archivos, consulta de notificaciones y verificacion de vencimientos.
- `admin/`: panel administrativo de Django.

El backend utiliza:

- Django como framework principal.
- Django REST Framework para los endpoints tipo API.
- SQLite como base de datos por defecto en desarrollo.
- `AUTH_USER_MODEL = users.User` como modelo de usuario personalizado.

### Frontend

El frontend usa React Router y actualmente expone estas rutas principales:

- `/login`
- `/register`
- `/dashboard`
- `/dashboard/cases`
- `/dashboard/permissions`

Durante desarrollo, Vite redirige las rutas `/users`, `/cases` y `/documents` hacia el backend local en `http://127.0.0.1:8000`.

## Modulos del backend

### `users`

Responsable de:

- login de usuarios
- registro de beneficiarios
- consulta del usuario autenticado
- consulta de profesores y beneficiarios
- gestion administrativa de usuarios

### `cases`

Responsable de:

- modelado de casos
- asignaciones de usuarios a casos
- estados, categorias y subclinicas
- aprobacion de casos
- rechazo de asignaciones
- trazabilidad mediante `CaseLog`

### `documents`

Responsable de:

- carga y descarga de documentos asociados a casos
- control de acceso a documentos
- verificacion de vencimientos
- notificaciones de proximidad o vencimiento
- consulta de notificaciones del usuario autenticado
- ejecucion manual del proceso de verificacion de vencimientos

## Requisitos del entorno

- Python 3.10 o superior
- Node.js 18 o superior
- npm 9 o superior

## Puesta en marcha

### 1. Backend

Desde la raiz del proyecto:

#### Windows (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Linux / macOS

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend disponible en:

- `http://127.0.0.1:8000`

### 2. Frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend disponible en:

- `http://127.0.0.1:5173`

## Flujo recomendado de uso en desarrollo

1. Levantar el backend.
2. Levantar el frontend.
3. Abrir `http://127.0.0.1:5173`.
4. Iniciar sesion con un usuario existente o registrar un beneficiario.
5. Gestionar casos, documentos y usuarios segun el rol autenticado.

## Credenciales de desarrollo

El proyecto incluye un comando de seed para crear usuarios de prueba:

```bash
cd backend
python manage.py seed_users
```

Credenciales de desarrollo esperadas:

- `admin / admin123`
- `advisor / advisor123`
- `professor / professor123`
- `student / student123`

## Comandos utiles

### Backend

```bash
cd backend
python manage.py check
python manage.py test
python manage.py seed_users
python manage.py seed_cases
python manage.py check_document_expirations
```

El comando `check_document_expirations` tambien acepta parametros opcionales:

```bash
python manage.py check_document_expirations --today 2026-04-27 --alert-days 3
```

### Frontend

```bash
cd frontend
npm run lint
npm run build
npm run preview
```

## Estructura principal del repositorio

```text
backend/
  manage.py
  lawclinic/
  users/
  cases/
  documents/
  media/
frontend/
  src/
  public/
docs/
README.md
```

## Notas tecnicas

- La base de datos por defecto es `backend/db.sqlite3`.
- Los archivos subidos se almacenan en `backend/media/`.
- Si cambias modelos, ejecuta:

```bash
python manage.py makemigrations
python manage.py migrate
```

- Si necesitas un entorno limpio de desarrollo, elimina `db.sqlite3` solo si sabes que no necesitas los datos actuales.
- Las notificaciones de vencimiento estan implementadas en backend y pueden probarse por API aunque la experiencia visual en frontend no este completamente acoplada.
