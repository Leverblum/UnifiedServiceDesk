# Unified Service Desk (MVP)

Sistema integral de gestión de tickets de soporte TI concebido bajo principios de **Clean Architecture** estructurado como un **Monolito Modular (Modular Monolith)**.

---

## 1. Patrones de Diseño GoF Implementados

| Patrón GoF | Capa / Módulo | Descripción y Responsabilidad |
| :--- | :--- | :--- |
| **Singleton** | `backend/core/database.py` | Gestiona de forma centralizada y segura en hilos (`threading.Lock`) la instancia de conexión, pool y `sessionmaker` de la base de datos relacional. |
| **Factory Method** | `backend/domain/factories/` | Instanciación polimórfica de tickets (`HardwareTicket`, `SoftwareTicket`, `AccessTicket`) con validación estricta de invariantes y prioridades automáticas. |
| **Repository** | `backend/repositories/` | Aísla totalmente el dominio y la fachada del ORM (SQLAlchemy) mediante `TicketRepositoryInterface` y `SQLAlchemyTicketRepository`. |
| **Facade** | `backend/services/service_desk_facade.py` | Orquesta todo el flujo de negocio (validaciones, creación, transiciones de estado, persistencia y eventos). Los routers de FastAPI interactúan exclusivamente con esta fachada. |
| **State** | `backend/domain/states/` | Máquina de estados (`OpenState`, `InProcessState`, `ResolvedState`, `ClosedState`) que encapsula las transiciones legales sin condicionales masivos (`if/elif`). |
| **Observer** | `backend/services/observers/` | Bus de eventos y suscriptores (`TicketSubject`) que notifica en tiempo real a `AuditLogObserver` (registro en BD) y `EmailNotifierObserver` (despacho simulado de correo). |

---

## 2. Tecnologías Utilizadas

- **Backend**: Python 3.14 / FastAPI (Asíncrono, Pydantic v2, Uvicorn).
- **ORM / Base de Datos**: SQLAlchemy 2.0 (PostgreSQL / SQLite).
- **Frontend**: React 19 + Vite + Tailwind CSS.
- **Arquitectura**: Clean Architecture & Monolito Modular.

---

## 3. Instrucciones de Ejecución

### Iniciar el Backend (FastAPI)
1. Abrir una terminal en la raíz del proyecto.
2. Ejecutar con el entorno virtual:
   ```powershell
   .\backend\venv\Scripts\uvicorn backend.main:app --reload --port 8000
   ```
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

---

## 4. Estructura del Proyecto

```text
UnifiedServiceDesk/
├── backend/
│   ├── api/
│   │   ├── dependencies.py             # Inyección de dependencias (Depends)
│   │   └── v1/
│   │       ├── endpoints/tickets.py    # Endpoints HTTP (consumen solo la Fachada)
│   │       └── router.py
│   ├── core/
│   │   ├── config.py                   # Pydantic Settings
│   │   └── database.py                 # DatabaseManager (Singleton)
│   ├── domain/
│   │   ├── models/                     # Modelos ORM (Ticket, AuditLog)
│   │   ├── schemas/                    # DTOs Pydantic
│   │   ├── states/                     # Patrón State
│   │   └── factories/                  # Patrón Factory Method
│   ├── repositories/                   # Patrón Repository (base & sqlalchemy)
│   ├── services/
│   │   ├── observers/                  # Patrón Observer (AuditLog & EmailNotifier)
│   │   └── service_desk_facade.py      # Patrón Facade
│   └── main.py                         # FastAPI App & Lifespan
├── frontend/
│   ├── src/
│   │   ├── components/                 # Tablero Kanban, Dashboard, Formularios, Auditoría
│   │   ├── services/api.js             # Cliente HTTP
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── tailwind.config.js
│   └── package.json
└── docs/
    └── architecture_guidelines.md      # Guía y diagramas arquitectónicos
```
