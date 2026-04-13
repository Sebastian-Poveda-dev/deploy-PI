# Clinica Juridica - Sistema de Gestion de Casos

Este proyecto es una aplicacion web para gestionar casos de una clinica juridica universitaria.

Permite:
- Registrar y autenticar usuarios.
- Gestionar roles (admin, advisor, professor, student, beneficiary).
- Crear, listar y actualizar casos.
- Aprobar casos y rechazar asignaciones segun reglas de negocio.
- Registrar documentos y trazabilidad (logs) por caso.

## Arquitectura

El repositorio esta dividido en dos aplicaciones:

- `backend/`: API REST en Django + Django REST Framework.
- `frontend/`: interfaz web en React + Vite.

Durante desarrollo, el frontend usa proxy de Vite para redirigir `/users`, `/cases` y `/documents` al backend en `http://127.0.0.1:8000`.

## Requisitos

- Python 3.10 o superior
- Node.js 18 o superior
- npm 9 o superior

## 1) Ejecutar Backend (Django)

Desde la raiz del proyecto:

### Windows (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Linux / macOS

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

## 2) Ejecutar Frontend (React + Vite)

En otra terminal, desde la raiz del proyecto:

```bash
cd frontend
npm install
npm run dev
```

Frontend disponible en:
- `http://127.0.0.1:5173`

## 3) Comandos utiles

### Backend

```bash
cd backend
python manage.py check
python manage.py test
```

### Frontend

```bash
cd frontend
npm run lint
npm run build
npm run preview
```

## Flujo recomendado de arranque

1. Levantar backend (`python manage.py runserver`).
2. Levantar frontend (`npm run dev`).
3. Abrir `http://127.0.0.1:5173`.
4. Iniciar sesion o registrar usuario segun permisos del flujo.

## Estructura principal

```text
backend/
  manage.py
  lawclinic/
  users/
  cases/
  documents/
frontend/
  src/
  public/
docs/
```

## Notas

- La base de datos por defecto es SQLite (`backend/db.sqlite3`).
- Si cambias modelos, ejecuta:

```bash
python manage.py makemigrations
python manage.py migrate
```

- Para un entorno limpio de desarrollo, elimina `db.sqlite3` solo si sabes que no necesitas los datos actuales.
