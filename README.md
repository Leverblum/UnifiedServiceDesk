# Unified Service Desk — Mesa de Ayuda Universitaria

Sistema integral de gestión de tickets de soporte TI y trámites académicos universitarios. Implementa **Clean Architecture** como **Monolito Modular** con **Control de Acceso Basado en Roles (RBAC)** y los 6 patrones de diseño GoF.

**Stack:** Python 3.14 + FastAPI + SQLAlchemy 2.0 (SQLite/PostgreSQL) · React 19 + Vite + Tailwind CSS

---

## Roles del Sistema — 5 Roles Oficiales

| Rol | Icono | Descripción | Acceso |
|-----|-------|-------------|--------|
| `STUDENT` | 🎓 | Estudiante universitario | Portal de autoservicio — solo sus propios tickets |
| `STAFF` | 🏫 | Personal administrativo / Docente | Portal de autoservicio — solo sus propios tickets |
| `IT_STUDENT_SUPPORT` | 📚 | TI Soporte Estudiantes | Tablero Kanban — atiende tickets estudiantiles |
| `IT_STAFF_SUPPORT` | 🛠️ | TI Soporte Personal & Campus | Tablero Kanban — atiende tickets de personal e infraestructura |
| `ADMIN` | 🛡️ | Administrador General | Acceso completo — métricas, usuarios, todos los tickets |

### Usuarios de Prueba (seed)

| Email | Rol | Nombre |
|-------|-----|--------|
| `admin@universidad.edu.co` | ADMIN | Ing. Andrés Valenzuela |
| `estudiante.camilo@universidad.edu.co` | STUDENT | Camilo Torres |
| `profesora.helena@universidad.edu.co` | STAFF | Dra. Helena Restrepo |
| `soporte.estudiantes@universidad.edu.co` | IT_STUDENT_SUPPORT | Mateo Rivas |
| `soporte.personal@universidad.edu.co` | IT_STAFF_SUPPORT | Ing. Laura Méndez |

**Contraseña de demo:** `UniServiceDesk2026!` (configurable en `SEED_DEFAULT_PASSWORD`)

---

## Vistas por Rol

### 🎓 STUDENT / 🏫 STAFF — Portal de Autoservicio
- Consulta y seguimiento **únicamente de sus propios tickets** (aislamiento de datos RF-08).
- Formulario de creación adaptativo según categoría (**Factory Method**).
- Puede solicitar reapertura formal de casos resueltos.
- No tiene acceso al tablero Kanban general.

### 📚 IT_STUDENT_SUPPORT / 🛠️ IT_STAFF_SUPPORT — Tablero Kanban
- Vista operativa con columnas `OPEN → IN_PROCESS → RESOLVED → CLOSED`.
- Filtros rápidos: todos los casos, cola sin asignar, asignados a mí.
- Autoasignación con un clic y reasignación entre técnicos.
- Transiciones de estado gobernadas por el **Patrón State**.

### 🛡️ ADMIN — Panel de Administración
- Control completo del sistema.
- Gestión de usuarios: alta, consulta y asignación de roles.
- Acceso a métricas globales (`GET /api/v1/tickets/metrics`).
- Puede reasignar y eliminar cualquier ticket.

---

## Categorías de Tickets

### Trámites Estudiantiles
| Categoría | Descripción | Metadatos obligatorios |
|-----------|-------------|----------------------|
| `CERTIFICADO` | Certificados de notas y constancias | `student_code`, `certificate_type` |
| `MATRICULA` | Ajustes de matrícula e inscripciones | `student_code`, `subject_or_program` |
| `RADICADO` | Peticiones formales, PQR | `request_type` |
| `CAMPUS_VIRTUAL` | Moodle, Teams, correo institucional | `platform_name` |

### Soporte TI para Personal
| Categoría | Descripción | Metadatos obligatorios |
|-----------|-------------|----------------------|
| `HARDWARE` | Equipos, proyectores, periféricos | `serial_number` o `device_type` |
| `SOFTWARE` | ERP, software de laboratorios | `software_name` |
| `ACCESS` | VPN, permisos de red, accesos | `target_system`, `system_role` |

---

## Patrones de Diseño GoF Implementados

| Patrón | Archivo principal | Descripción |
|--------|-------------------|-------------|
| **Singleton** | `backend/core/database.py` | `DatabaseManager` — pool de conexiones único, thread-safe con `threading.Lock` |
| **Factory Method** | `backend/domain/factories/ticket_factories.py` | `TicketFactoryRegistry` + 7 fábricas concretas por categoría |
| **Repository** | `backend/repositories/` | `SQLAlchemyTicketRepository` y `SQLAlchemyUserRepository` — desacoplan dominio del ORM |
| **Facade** | `backend/services/service_desk_facade.py` | `ServiceDeskFacade` — punto único de orquestación para todos los endpoints |
| **State** | `backend/domain/states/ticket_states.py` | `OpenState`, `InProcessState`, `ResolvedState`, `ClosedState` |
| **Observer** | `backend/services/observers/` | `TicketSubject`, `AuditLogObserver`, `EmailNotifierObserver` |

---

## Seguridad

| Defecto | Corrección aplicada |
|---------|-------------------|
| DEF-01 Contraseñas en texto plano | Hashing **Argon2id** (`argon2-cffi`) — almacenado como `$argon2id$...` |
| DEF-02 Credenciales hardcodeadas | Sin `"12345"` en código fuente; secretos en `.env` vía `SEED_DEFAULT_PASSWORD` |
| DEF-03 Sin autenticación real | **JWT (PyJWT HS256)** firmado con `sub`, `role`, `iat`, `exp`; endpoint `GET /me` |
| DEF-04 Sesión insegura en frontend | Token JWT en **memoria del módulo** `api.js` — nunca en `localStorage` |
| DEF-05 Roles inconsistentes | 5 roles oficiales únicos; eliminados `USER`, `AGENT`, `IT_SUPPORT` |

---

## Requisitos Previos

- Python 3.10+ (probado con 3.14.4)
- Node.js 18+ (probado con v25.9.0)
- pip

---

## Instalación y Ejecución

### 1. Clonar y configurar variables de entorno

```bash
git clone https://github.com/Leverblum/UnifiedServiceDesk.git
cd UnifiedServiceDesk

# Copiar la plantilla de entorno
cp backend/.env.example backend/.env
```

Editar `backend/.env` con al menos estos valores:

```env
DATABASE_URL=sqlite:///./unified_service_desk.db
JWT_SECRET_KEY=cambia_esto_por_un_valor_aleatorio_seguro
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
SEED_DEFAULT_PASSWORD=UniServiceDesk2026!
```

> Genera un JWT_SECRET_KEY seguro con:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 2. Backend (FastAPI)

```bash
# Instalar dependencias
pip install -r backend/requirements.txt

# Iniciar el servidor (desde la raíz del proyecto)
uvicorn backend.main:app --reload --port 8000
```

El servidor siembra automáticamente los 5 usuarios de prueba con contraseñas hasheadas al arrancar.

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

> **Nota Windows (PowerShell):**
> ```powershell
> $env:PYTHONPATH = $pwd
> & "python" -m uvicorn backend.main:app --reload --port 8000
> ```

### 3. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend disponible en http://localhost:5173

Opcionalmente, crea `frontend/.env` para configurar la contraseña del login rápido:
```env
VITE_DEMO_PASSWORD=UniServiceDesk2026!
```

### 4. Ejecutar pruebas automatizadas

```bash
# Desde la raíz del proyecto
# Windows:
set PYTHONPATH=%cd%
python -m pytest backend/tests/ -v --tb=short

# Linux/Mac:
PYTHONPATH=$(pwd) python -m pytest backend/tests/ -v --tb=short
```

Resultado esperado: **62 passed, 0 failed**

> Si al arrancar el backend el login falla con 401, elimina la BD en disco
> (`unified_service_desk.db`) para que se recree con contraseñas hasheadas:
> ```bash
> rm unified_service_desk.db   # o del en Windows
> ```

---

## Endpoints Principales de la API

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/users/login` | Login — retorna JWT Bearer | Pública |
| `GET` | `/api/v1/users/me` | Usuario autenticado desde token | Bearer |
| `GET` | `/api/v1/users/` | Listar usuarios (filtrable por rol) | Pública |
| `POST` | `/api/v1/users/` | Crear usuario | Pública |
| `POST` | `/api/v1/users/seed` | Sembrar 5 usuarios de prueba | Pública |
| `GET` | `/api/v1/tickets/` | Listar tickets (filtros + paginación) | Pública |
| `POST` | `/api/v1/tickets/` | Crear ticket (Factory Method) | Pública |
| `GET` | `/api/v1/tickets/metrics` | Métricas e indicadores del sistema | Pública |
| `POST` | `/api/v1/tickets/{id}/assign` | Asignar ticket a técnico TI | Pública |
| `PATCH` | `/api/v1/tickets/{id}/status` | Transicionar estado (State Pattern) | Pública |
| `GET` | `/api/v1/tickets/{id}/audit-logs` | Historial de auditoría (Observer) | Pública |
| `GET` | `/health` | Health check del servicio | Pública |

---

## Estructura del Proyecto

```
UnifiedServiceDesk/
├── backend/
│   ├── api/
│   │   ├── dependencies.py          # DI: sesión, repositorios, JWT, RBAC
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── users.py         # Login JWT, /me, CRUD usuarios
│   │           └── tickets.py       # CRUD tickets, métricas, auditoría
│   ├── core/
│   │   ├── config.py                # Settings con validación JWT_SECRET_KEY
│   │   ├── database.py              # Singleton DatabaseManager
│   │   └── security.py              # hash_password, verify_password, JWT
│   ├── domain/
│   │   ├── factories/               # Factory Method (7 fábricas concretas)
│   │   ├── models/                  # ORM: UserModel, TicketModel, AuditLogModel
│   │   ├── schemas/                 # DTOs Pydantic (UserRole, TokenResponse, etc.)
│   │   └── states/                  # State Pattern (4 estados de ticket)
│   ├── repositories/                # Repository Pattern (Ticket, User)
│   ├── services/
│   │   ├── service_desk_facade.py   # Facade + login() con JWT + métricas
│   │   ├── exceptions.py            # Excepciones de dominio
│   │   └── observers/               # Observer (AuditLog + EmailNotifier)
│   ├── tests/
│   │   ├── conftest.py              # Fixtures pytest (BD en memoria, tokens JWT)
│   │   ├── test_user_auth.py        # CP-05, CP-10, CP-11, CP-12
│   │   ├── test_rbac.py             # CP-06, CP-09
│   │   └── test_university.py       # CP-01..04, CP-07..08, CP-13, CP-14, CP-17
│   ├── .env.example                 # Plantilla de variables de entorno
│   ├── pytest.ini
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── services/
│       │   └── api.js               # Cliente HTTP con Bearer token en memoria
│       ├── App.jsx                  # Shell principal — sin localStorage de email
│       └── components/
│           ├── LoginModal.jsx       # Login con contraseña real (VITE_DEMO_PASSWORD)
│           ├── UserPortal.jsx       # Vista STUDENT / STAFF
│           ├── KanbanBoard.jsx      # Vista IT_STUDENT_SUPPORT / IT_STAFF_SUPPORT
│           ├── AdminPanel.jsx       # Vista ADMIN
│           ├── Dashboard.jsx        # Métricas y KPIs
│           ├── Navbar.jsx           # Barra de navegación por rol
│           ├── TicketFormModal.jsx  # Creación de ticket (Factory Method)
│           └── AuditLogModal.jsx    # Historial de auditoría (Observer)
└── docs/
    ├── architecture_guidelines.md   # Guía arquitectónica detallada
    └── REPORTE_PRUEBAS_QA.md        # Reporte QA — 62 casos de prueba
```

---

## Cobertura de Pruebas QA

| ID | Requisito | Descripción |
|----|-----------|-------------|
| CP-01 | RF-01 | Creación de ticket con ID único autoincremental |
| CP-02 | RF-02 | 7 categorías + 4 prioridades (11 tests parametrizados) |
| CP-03 | RF-03 | Asignación y reasignación a técnico TI |
| CP-04 | RF-04 | Transiciones de estado válidas e inválidas (State Pattern) |
| CP-05 | RF-05 | Login JWT: 200 + token válido / 401 en inválido |
| CP-06 | RF-05 | RBAC 5 roles: 200/403 según permisos |
| CP-07 | RF-06 | Observer: ≥3 eventos en audit log por ticket |
| CP-08 | RF-07 | Métricas matemáticamente consistentes con la BD |
| CP-09 | RF-08 | Aislamiento: STUDENT solo ve sus propios tickets |
| CP-10 | DEF-01 | Hash `$argon2id$` en BD, salts únicos por usuario |
| CP-11 | DEF-03 | JWT: 401 sin token / con firma alterada / expirado |
| CP-12 | DEF-02 | 0 contraseñas hardcodeadas en archivos .py y .js |
| CP-13 | RNF-02 | Todos los endpoints responden en < 2.0 s |
| CP-14 | Staging | `/health` → 200 + status: healthy |
| CP-17 | RNF-06 | Integridad referencial: 404/400/422 controlados |

Ver reporte completo en [`docs/REPORTE_PRUEBAS_QA.md`](docs/REPORTE_PRUEBAS_QA.md).
