# Unified Service Desk (MVP con Roles y RBAC)

Sistema integral de gestión de tickets de soporte TI concebido bajo principios de **Clean Architecture**, estructurado como un **Monolito Modular (Modular Monolith)** e implementando **Control de Acceso Basado en Roles (RBAC)** con vistas separadas y especializadas según el perfil del usuario.

---

## 1. Vistas y Roles del Sistema (RBAC)

La aplicación incluye un **Selector de Persona / Rol** en la barra superior (Navbar) que permite alternar dinámicamente y sin fricciones entre los distintos roles para pruebas inmediatas:

### 👤 1. Vista de Usuario Solicitante (`USER`)
- **Personas de demostración:** Carlos Gómez (Finanzas & Contabilidad), María López (Marketing & Comunicaciones).
- **Funcionalidades:**
  - **Portal de Autoservicio (`UserPortal.jsx`):** Consulta y seguimiento en tiempo real **únicamente de los tickets creados por el usuario**.
  - Tarjetas de estado con información clara sobre qué **especialista técnico de TI** está atendiendo el caso (o si está en espera de asignación).
  - Formulario de creación adaptativo (**Factory Method**) con pre-asignación automática del solicitante.
  - Opción de solicitar **reapertura formal** de casos resueltos o cerrados si la falla persiste.
  - El usuario solicitante **no** tiene acceso a la cola general de TI ni puede forzar resoluciones técnicas arbitrarias.

### 🛠️ 2. Vista de Mesa de Ayuda TI (`IT_SUPPORT`)
- **Personas de demostración:** Laura Técnico (Mesa de Ayuda Nivel 1), David Sistemas (Infraestructura & Servidores).
- **Funcionalidades:**
  - **Tablero Kanban Operativo (`KanbanBoard.jsx`):** Flujo de trabajo dividido por estados (`OPEN` $\rightarrow$ `IN_PROCESS` $\rightarrow$ `RESOLVED` $\rightarrow$ `CLOSED`).
  - **Filtros de Triage rápido:** "Todos los Casos", "Cola Sin Asignar" y "Asignados a Mí".
  - **Asignación y Reasignación técnica:** Botón de un solo clic *"Tomar Ticket ✋"* para autoasignarse incidencias y selector desplegable para transferir casos entre especialistas de TI.
  - Gestión de transiciones gobernadas por el **Patrón State**.
  - Inspección de trazabilidad y correos notificados (**Patrón Observer**).

### 🛡️ 3. Vista de Administración Global (`ADMIN`)
- **Persona de demostración:** Andrés Admin (Dirección de Tecnología).
- **Funcionalidades:**
  - Control absoluto del sistema.
  - **Panel de Gestión de Usuarios y Directorio RBAC (`AdminPanel.jsx`):**
    - Directorio completo de usuarios con métricas de tickets creados y tickets asignados.
    - Formulario para dar de alta nuevos usuarios y asignarles roles (`USER`, `IT_SUPPORT`, `ADMIN`).
  - Capacidad de reasignar cualquier ticket, eliminar incidencias y consultar métricas globales de soporte y carga operativa por técnico.

---

## 2. Patrones de Diseño GoF Implementados

| Patrón GoF | Capa / Módulo | Descripción y Responsabilidad |
| :--- | :--- | :--- |
| **Singleton** | `backend/core/database.py` | Gestiona de forma centralizada y segura en hilos (`threading.Lock`) la instancia de conexión, pool y `sessionmaker` de la base de datos relacional. |
| **Factory Method** | `backend/domain/factories/` | Instanciación polimórfica de tickets (`HardwareTicket`, `SoftwareTicket`, `AccessTicket`) con validación de invariantes, prioridades automáticas y asociación al usuario solicitante (`created_by_id`). |
| **Repository** | `backend/repositories/` | Aísla totalmente el dominio y la fachada del ORM (SQLAlchemy) mediante `TicketRepositoryInterface` y `UserRepositoryInterface`. |
| **Facade** | `backend/services/service_desk_facade.py` | Orquesta todo el flujo de negocio: validaciones, creación, asignación a especialistas, verificación RBAC, transiciones de estado, persistencia y eventos. Los controladores de FastAPI interactúan exclusivamente con esta fachada. |
| **State** | `backend/domain/states/` | Máquina de estados (`OpenState`, `InProcessState`, `ResolvedState`, `ClosedState`) que encapsula las transiciones legales sin condicionales masivos (`if/elif`). |
| **Observer** | `backend/services/observers/` | Bus de eventos y suscriptores (`TicketSubject`) que notifica en tiempo real a `AuditLogObserver` (registro en BD) y `EmailNotifierObserver` (despacho simulado de correo al solicitante y al técnico asignado). |

---

## 3. Tecnologías Utilizadas

- **Backend:** Python 3.14 / FastAPI (Asíncrono, Pydantic v2, Uvicorn).
- **ORM / Base de Datos:** SQLAlchemy 2.0 (PostgreSQL / SQLite).
- **Frontend:** React 19 + Vite + Tailwind CSS.
- **Arquitectura:** Clean Architecture & Monolito Modular con RBAC.

---

## 4. Instrucciones de Ejecución

### Iniciar el Backend (FastAPI)
1. Abrir una terminal en la raíz del proyecto.
2. Ejecutar con el entorno virtual:
   ```powershell
   .\backend\venv\Scripts\uvicorn backend.main:app --reload --port 8000
   ```
   El backend usa por defecto `unified_service_desk.db` (SQLite) en la raíz del proyecto.
   Para usar PostgreSQL, configura `DATABASE_URL` en el entorno o en `.env`; el servidor
   PostgreSQL debe aceptar conexiones con codificación UTF-8.
3. Documentación interactiva de la API:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Iniciar el Frontend (React + Vite)
1. Abrir una segunda terminal en la raíz del proyecto.
2. Iniciar el servidor de desarrollo:
   ```powershell
   npm --prefix frontend run dev
   ```
3. Abrir en el navegador: [http://localhost:5173](http://localhost:5173)

### Ejecutar Pruebas Automatizadas de Integración y RBAC
```powershell
.\backend\venv\Scripts\python backend/tests/test_rbac.py
.\backend\venv\Scripts\python backend/tests/test_user_auth.py
```

---

## 5. Estructura del Proyecto

```text
UnifiedServiceDesk/
├── backend/
│   ├── api/
│   │   ├── dependencies.py             # Inyección de dependencias (Depends)
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── tickets.py          # Endpoints HTTP de Tickets (consumen la Fachada)
│   │       │   └── users.py            # Endpoints HTTP de Usuarios y RBAC
│   │       └── router.py
│   ├── core/
│   │   ├── config.py                   # Pydantic Settings
│   │   └── database.py                 # DatabaseManager (Singleton)
│   ├── domain/
│   │   ├── models/                     # Modelos ORM (User, Ticket, AuditLog)
│   │   ├── schemas/                    # DTOs Pydantic (User, Ticket, Enums)
│   │   ├── states/                     # Patrón State (Open, InProcess, Resolved, Closed)
│   │   └── factories/                  # Patrón Factory Method (HW, SW, Access)
│   ├── repositories/                   # Patrón Repository (TicketRepository, UserRepository)
│   ├── services/
│   │   ├── observers/                  # Patrón Observer (AuditLog & EmailNotifier)
│   │   ├── exceptions.py               # Excepciones de negocio y autorización
│   │   └── service_desk_facade.py      # Patrón Facade (Punto central de orquestación)
│   ├── tests/
│   │   └── test_rbac.py                # Pruebas automatizadas de roles y flujos
│   └── main.py                         # FastAPI App & Lifespan
├── frontend/
│   ├── src/
│   │   ├── components/                 
│   │   │   ├── UserPortal.jsx          # Vista de Usuario Solicitante (USER)
│   │   │   ├── KanbanBoard.jsx         # Vista de Mesa de Ayuda TI (IT_SUPPORT)
│   │   │   ├── AdminPanel.jsx          # Vista de Administración Global (ADMIN)
│   │   │   ├── Dashboard.jsx           # Métricas y KPIs de soporte
│   │   │   ├── Navbar.jsx              # Barra con Selector de Rol / Persona
│   │   │   ├── TicketFormModal.jsx     # Creación polimórfica (Factory Method)
│   │   │   └── AuditLogModal.jsx       # Trazabilidad y Notificaciones (Observer)
│   │   ├── services/api.js             # Cliente HTTP Axios/Fetch
│   │   ├── App.jsx                     # Shell principal reactivo
│   │   └── main.jsx
│   ├── tailwind.config.js
│   └── package.json
└── docs/
    └── architecture_guidelines.md      # Guía y diagramas arquitectónicos
```
