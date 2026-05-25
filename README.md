# Consultorio Jurídico - Sistema de Gestión de Casos

Sistema web para el consultorio jurídico de la Universidad Icesi. Permite gestionar casos legales de beneficiarios, asignar estudiantes y asesores, hacer seguimiento de documentos y comunicarse internamente entre los usuarios del consultorio.

## Demo en línea

La aplicación está desplegada en:

**https://deploypi-gules.vercel.app/**

## Roles del sistema

| Rol | Descripción |
|---|---|
| `admin` | Gestiona usuarios, aprueba y cancela casos |
| `advisor` | Supervisa casos asignados a su sala |
| `student` | Atiende los casos asignados, sube documentos y registra progreso |
| `beneficiary` | Solicita atención y consulta el estado de sus casos |

## Funcionalidades principales

- Registro de beneficiarios y autenticación por roles
- Creación y aprobación de casos, con asignación automática de estudiante y asesor
- Seguimiento del caso: progreso, bitácora de actividad y documentos adjuntos
- Solicitud y revisión de reasignación de casos
- Notificaciones de vencimiento de documentos
- Chat interno entre usuarios del consultorio
- Métricas de casos por categoría, estado y sala

## Tecnologías

- **Backend**: Django 4.2 + Django REST Framework + Daphne (ASGI/WebSockets)
- **Frontend**: React 19 + Vite + Tailwind CSS
- **Base de datos**: PostgreSQL en producción, SQLite en desarrollo

## Correr localmente

### Requisitos

- Python 3.10+
- Node.js 18+

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo --flush   # carga datos de demostración
python manage.py runserver
```

### Frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Abrir **http://localhost:5173**

## Datos de demostración

El comando `seed_demo --flush` limpia la base de datos y crea:

- 1 administrador, 6 asesores (uno por sala), 8 estudiantes, 10 beneficiarios
- 15 casos con distintos estados, documentos y progreso registrado
- 3 solicitudes de reasignación pendientes

Credenciales de ejemplo:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `Admin1234!` | Administrador |
| `advisorX` | `Advisor1234!` | Asesor (X = 1 al 6) |
| `studentX` | `Student1234!` | Estudiante (X = 1 al 8) |
| `beneficiaryX` | `Beneficiary1234!` | Beneficiario (X = 1 al 10) |

## Estructura del repositorio

```
backend/
  lawclinic/      # configuración del proyecto Django
  users/          # autenticación, usuarios y roles
  cases/          # casos, asignaciones, progreso y logs
  documents/      # documentos y notificaciones de vencimiento
  communications/ # chat interno
  metrics/        # métricas y reportes
frontend/
  src/
    components/
    pages/
    services/
```
