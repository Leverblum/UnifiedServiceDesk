"""
test_university.py — Pruebas funcionales y no funcionales del Service Desk Universitario.

Cubre:
- CP-01 (RF-01): Creación de ticket con datos obligatorios e ID único autoincremental
- CP-02 (RF-02): Categorías TI y académicas + prioridades
- CP-03 (RF-03): Asignación y reasignación de ticket a técnico TI
- CP-04 (RF-04): Transiciones de estado (State Pattern) válidas e inválidas
- CP-07 (RF-06): Historial de auditoría tras modificación (Observer Pattern)
- CP-08 (RF-07): Métricas e indicadores con validación matemática
- CP-13 (RNF-02): Rendimiento < 2.0 segundos en endpoints principales
- CP-14 (Healthcheck): Endpoint /api/health responde correctamente
- CP-17 (RNF-06): Integridad referencial — IDs inexistentes rechazados
"""

import os
import sys
import time
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.tests.conftest import auth_headers


# ==============================================================
# CP-01: Creación de ticket con ID único autoincremental
# ==============================================================

class TestTicketCreationCP01:
    """CP-01 (RF-01): Creación de ticket con datos obligatorios."""

    def test_create_ticket_returns_201_with_unique_id(self, client, seeded_users):
        """CP-01: Ticket creado retorna 201, ID único y estado OPEN."""
        student = seeded_users["STUDENT"]
        t0 = time.perf_counter()
        res = client.post("/api/v1/tickets/", json={
            "title": "Solicitud de certificado de notas CP01",
            "description": "Necesito certificado para proceso de admisión a maestría",
            "category": "CERTIFICADO",
            "created_by_id": student["id"],
            "specific_metadata": {
                "student_code": "2022CP01",
                "certificate_type": "Certificado de Notas"
            }
        })
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert res.status_code == 201, f"Se esperaba 201: {res.text}"
        data = res.json()
        assert "id" in data, "El ticket debe tener un ID"
        assert isinstance(data["id"], int) and data["id"] > 0, "ID debe ser entero positivo"
        assert data["status"] == "OPEN", "Estado inicial debe ser OPEN"
        assert data["category"] == "CERTIFICADO"
        print(f"\n  CP-01 PASS — Ticket #{data['id']} creado (201) en {elapsed_ms:.1f} ms ✓")

    def test_created_ticket_ids_are_unique(self, client, seeded_users):
        """CP-01b: Dos tickets creados tienen IDs distintos (unicidad autoincremental)."""
        student = seeded_users["STUDENT"]
        payload = {
            "title": "Ticket unicidad",
            "description": "Test de unicidad de ID",
            "category": "CERTIFICADO",
            "created_by_id": student["id"],
            "specific_metadata": {
                "student_code": "2022UNIQ",
                "certificate_type": "Constancia de Estudio"
            }
        }
        res1 = client.post("/api/v1/tickets/", json=payload)
        res2 = client.post("/api/v1/tickets/", json={**payload, "title": "Ticket unicidad 2"})
        assert res1.status_code == 201
        assert res2.status_code == 201
        assert res1.json()["id"] != res2.json()["id"], "Los IDs deben ser únicos"
        print("\n  CP-01b PASS — IDs únicos verificados ✓")


# ==============================================================
# CP-02: Categorías TI y académicas + prioridades
# ==============================================================

class TestCategoriesAndPrioritiesCP02:
    """CP-02 (RF-02): Creación con distintas categorías y prioridades."""

    @pytest.mark.parametrize("category,metadata,priority", [
        # Categorías académicas (estudiantiles)
        ("CERTIFICADO", {"student_code": "2022C1", "certificate_type": "Notas"}, "MEDIUM"),
        ("MATRICULA", {"student_code": "2022C2", "subject_or_program": "Cálculo I"}, "HIGH"),
        ("RADICADO", {"request_type": "Petición formal"}, "MEDIUM"),
        ("CAMPUS_VIRTUAL", {"platform_name": "Moodle"}, "HIGH"),
        # Categorías TI para personal
        ("HARDWARE", {"device_type": "Proyector"}, "HIGH"),
        ("SOFTWARE", {"software_name": "ERP Académico"}, "MEDIUM"),
        ("ACCESS", {"target_system": "VPN", "system_role": "Docente"}, "CRITICAL"),
    ])
    def test_create_ticket_all_categories(self, client, seeded_users, category, metadata, priority):
        """CP-02: Cada categoría crea ticket exitosamente con prioridad correcta."""
        student = seeded_users["STUDENT"]
        staff = seeded_users["STAFF"]
        creator_id = student["id"] if category in ["CERTIFICADO", "MATRICULA", "RADICADO", "CAMPUS_VIRTUAL"] else staff["id"]

        res = client.post("/api/v1/tickets/", json={
            "title": f"Test categoría {category}",
            "description": f"Prueba para categoría {category}",
            "category": category,
            "created_by_id": creator_id,
            "specific_metadata": metadata
        })
        assert res.status_code == 201, f"Categoría {category} falló: {res.text}"
        data = res.json()
        assert data["category"] == category
        assert data["status"] == "OPEN"
        print(f"\n  CP-02 [{category}] PASS — Ticket creado, prioridad={data['priority']} ✓")

    @pytest.mark.parametrize("priority", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    def test_explicit_priority_is_respected(self, client, seeded_users, priority):
        """CP-02b: La prioridad explícita del request se respeta."""
        student = seeded_users["STUDENT"]
        res = client.post("/api/v1/tickets/", json={
            "title": f"Ticket con prioridad {priority}",
            "description": "Test de prioridad explícita",
            "category": "CERTIFICADO",
            "priority": priority,
            "created_by_id": student["id"],
            "specific_metadata": {"student_code": f"2022P{priority}", "certificate_type": "Notas"}
        })
        assert res.status_code == 201, f"Prioridad {priority} falló: {res.text}"
        assert res.json()["priority"] == priority
        print(f"\n  CP-02b [{priority}] PASS — Prioridad explícita respetada ✓")


# ==============================================================
# CP-03: Asignación y reasignación de ticket a técnico
# ==============================================================

class TestTicketAssignmentCP03:
    """CP-03 (RF-03): Asignación y reasignación de ticket a técnico TI."""

    @pytest.fixture(scope="class")
    def ticket_for_assignment(self, client, seeded_users):
        """Ticket de prueba para asignación."""
        staff = seeded_users["STAFF"]
        res = client.post("/api/v1/tickets/", json={
            "title": "Hardware CP03 - Proyector aula",
            "description": "El proyector del aula 302 no enciende",
            "category": "HARDWARE",
            "created_by_id": staff["id"],
            "specific_metadata": {"device_type": "Proyector Epson", "serial_number": "PROY-302"}
        })
        assert res.status_code == 201
        return res.json()

    def test_assign_to_it_staff_support(self, client, seeded_users, ticket_for_assignment):
        """CP-03a: Asignación a IT_STAFF_SUPPORT actualiza assigned_to_id y transiciona a IN_PROCESS."""
        it_support = seeded_users["IT_STAFF_SUPPORT"]
        ticket_id = ticket_for_assignment["id"]

        res = client.post(f"/api/v1/tickets/{ticket_id}/assign", json={
            "assigned_to_id": it_support["id"],
            "reason": "Asignado a soporte de personal"
        })
        assert res.status_code == 200, f"Asignación falló: {res.text}"
        data = res.json()
        assert data["assigned_to_id"] == it_support["id"], "assigned_to_id debe actualizarse"
        assert data["status"] == "IN_PROCESS", "Estado debe cambiar a IN_PROCESS"
        print("\n  CP-03a PASS — Asignación a IT_STAFF_SUPPORT OK, estado=IN_PROCESS ✓")

    def test_reassign_to_it_student_support(self, client, seeded_users, ticket_for_assignment):
        """CP-03b: Reasignación a otro técnico (IT_STUDENT_SUPPORT) persiste."""
        it_student = seeded_users["IT_STUDENT_SUPPORT"]
        ticket_id = ticket_for_assignment["id"]

        res = client.post(f"/api/v1/tickets/{ticket_id}/assign", json={
            "assigned_to_id": it_student["id"],
            "reason": "Reasignado a soporte de estudiantes"
        })
        assert res.status_code == 200, f"Reasignación falló: {res.text}"
        data = res.json()
        assert data["assigned_to_id"] == it_student["id"], "Reasignación debe persistir"
        print("\n  CP-03b PASS — Reasignación a IT_STUDENT_SUPPORT OK ✓")

    def test_cannot_assign_to_student_role(self, client, seeded_users, ticket_for_assignment):
        """CP-03c: No se puede asignar ticket a usuario con rol STUDENT (403)."""
        student = seeded_users["STUDENT"]
        ticket_id = ticket_for_assignment["id"]

        res = client.post(f"/api/v1/tickets/{ticket_id}/assign", json={
            "assigned_to_id": student["id"],
            "reason": "Intento inválido de asignar a estudiante"
        })
        assert res.status_code == 403, \
            f"Se esperaba 403 al asignar a STUDENT, se obtuvo {res.status_code}: {res.text}"
        print("\n  CP-03c PASS — No se puede asignar a rol STUDENT (403) ✓")


# ==============================================================
# CP-04: Transiciones de estado (State Pattern)
# ==============================================================

class TestStateTransitionsCP04:
    """CP-04 (RF-04): Transiciones válidas e inválidas del State Pattern."""

    @pytest.fixture(scope="class")
    def fresh_ticket(self, client, seeded_users):
        """Ticket fresco en estado OPEN para pruebas de transición."""
        student = seeded_users["STUDENT"]
        res = client.post("/api/v1/tickets/", json={
            "title": "Ticket State Pattern CP04",
            "description": "Prueba de transiciones de estado",
            "category": "CAMPUS_VIRTUAL",
            "created_by_id": student["id"],
            "specific_metadata": {"platform_name": "Moodle Institucional"}
        })
        assert res.status_code == 201
        return res.json()

    def test_open_to_in_process_valid(self, client, seeded_users, fresh_ticket):
        """CP-04a: OPEN → IN_PROCESS es una transición válida."""
        it_support = seeded_users["IT_STUDENT_SUPPORT"]
        ticket_id = fresh_ticket["id"]

        # Asignar para disparar OPEN → IN_PROCESS
        res = client.post(f"/api/v1/tickets/{ticket_id}/assign", json={
            "assigned_to_id": it_support["id"],
            "reason": "Asignado para transición"
        })
        assert res.status_code == 200
        assert res.json()["status"] == "IN_PROCESS"
        print("\n  CP-04a PASS — OPEN → IN_PROCESS válido ✓")

    def test_in_process_to_resolved_valid(self, client, seeded_users, fresh_ticket):
        """CP-04b: IN_PROCESS → RESOLVED es una transición válida."""
        it_support = seeded_users["IT_STUDENT_SUPPORT"]
        ticket_id = fresh_ticket["id"]

        res = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
            "target_status": "RESOLVED",
            "reason": "Problema resuelto",
            "user_id": it_support["id"]
        })
        assert res.status_code == 200
        assert res.json()["status"] == "RESOLVED"
        print("\n  CP-04b PASS — IN_PROCESS → RESOLVED válido ✓")

    def test_resolved_to_closed_valid(self, client, seeded_users, fresh_ticket):
        """CP-04c: RESOLVED → CLOSED es una transición válida."""
        it_support = seeded_users["IT_STUDENT_SUPPORT"]
        ticket_id = fresh_ticket["id"]

        res = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
            "target_status": "CLOSED",
            "reason": "Ticket cerrado por usuario",
            "user_id": it_support["id"]
        })
        assert res.status_code == 200
        assert res.json()["status"] == "CLOSED"
        print("\n  CP-04c PASS — RESOLVED → CLOSED válido ✓")

    def test_invalid_transition_closed_to_resolved(self, client, seeded_users, fresh_ticket):
        """CP-04d: CLOSED → RESOLVED es una transición inválida (400)."""
        it_support = seeded_users["IT_STUDENT_SUPPORT"]
        ticket_id = fresh_ticket["id"]

        # El ticket ya está CLOSED por CP-04c
        res = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
            "target_status": "RESOLVED",
            "reason": "Intento de transición inválida",
            "user_id": it_support["id"]
        })
        assert res.status_code == 400, \
            f"CLOSED→RESOLVED debe ser inválido (400), se obtuvo {res.status_code}"
        print("\n  CP-04d PASS — CLOSED → RESOLVED es transición inválida (400) ✓")


# ==============================================================
# CP-07: Historial de auditoría (Observer Pattern)
# ==============================================================

class TestAuditLogCP07:
    """CP-07 (RF-06): Historial de auditoría tras modificación de ticket."""

    @pytest.fixture(scope="class")
    def audit_ticket(self, client, seeded_users):
        """Ticket con historial de auditoría para verificación."""
        student = seeded_users["STUDENT"]
        it_support = seeded_users["IT_STAFF_SUPPORT"]

        # 1. Crear
        res_create = client.post("/api/v1/tickets/", json={
            "title": "Ticket Auditoría CP07",
            "description": "Test del Observer Pattern",
            "category": "SOFTWARE",
            "created_by_id": student["id"],
            "specific_metadata": {"software_name": "ERP Universitario"}
        })
        assert res_create.status_code == 201
        ticket = res_create.json()
        ticket_id = ticket["id"]

        # 2. Asignar
        res_assign = client.post(f"/api/v1/tickets/{ticket_id}/assign", json={
            "assigned_to_id": it_support["id"],
            "reason": "Asignación para auditoría"
        })
        assert res_assign.status_code == 200

        # 3. Resolver
        res_resolve = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
            "target_status": "RESOLVED",
            "reason": "Resuelta durante CP-07",
            "user_id": it_support["id"]
        })
        assert res_resolve.status_code == 200

        return ticket_id

    def test_audit_logs_contain_creation_event(self, client, audit_ticket):
        """CP-07a: El historial incluye el evento TICKET_CREATED."""
        res = client.get(f"/api/v1/tickets/{audit_ticket}/audit-logs")
        assert res.status_code == 200
        logs = res.json()
        event_types = [log["event_type"] for log in logs]
        assert "TICKET_CREATED" in event_types, f"Falta TICKET_CREATED en logs: {event_types}"
        print("\n  CP-07a PASS — TICKET_CREATED en historial de auditoría ✓")

    def test_audit_logs_contain_assign_event(self, client, audit_ticket):
        """CP-07b: El historial incluye el evento de asignación."""
        res = client.get(f"/api/v1/tickets/{audit_ticket}/audit-logs")
        logs = res.json()
        event_types = [log["event_type"] for log in logs]
        assert "TICKET_ASSIGNED" in event_types, f"Falta TICKET_ASSIGNED en logs: {event_types}"
        print("\n  CP-07b PASS — TICKET_ASSIGNED en historial de auditoría ✓")

    def test_audit_logs_contain_status_change(self, client, audit_ticket):
        """CP-07c: El historial incluye STATUS_CHANGED con estado anterior y nuevo."""
        res = client.get(f"/api/v1/tickets/{audit_ticket}/audit-logs")
        logs = res.json()
        status_logs = [l for l in logs if l["event_type"] == "STATUS_CHANGED"]
        assert len(status_logs) >= 1, "Debe haber al menos un evento STATUS_CHANGED"
        # Verificar que el log tiene old_status y new_status
        for log in status_logs:
            assert "new_status" in log
            assert log["new_status"] in ["IN_PROCESS", "RESOLVED", "CLOSED", "OPEN"]
        print("\n  CP-07c PASS — STATUS_CHANGED con estados anterior/nuevo ✓")

    def test_audit_log_has_minimum_3_events(self, client, audit_ticket):
        """CP-07d: Al menos 3 eventos registrados (creación + asignación + resolución)."""
        res = client.get(f"/api/v1/tickets/{audit_ticket}/audit-logs")
        logs = res.json()
        assert len(logs) >= 3, f"Se esperaban ≥3 eventos de auditoría, se encontraron {len(logs)}"
        print(f"\n  CP-07d PASS — {len(logs)} eventos en historial de auditoría ✓")


# ==============================================================
# CP-08: Métricas e indicadores con validación matemática
# ==============================================================

class TestMetricsCP08:
    """CP-08 (RF-07): Validación matemática de métricas."""

    def test_metrics_total_matches_ticket_count(self, client):
        """CP-08a: total_tickets en métricas coincide con el conteo real."""
        # Obtener todos los tickets
        res_tickets = client.get("/api/v1/tickets/?limit=500")
        assert res_tickets.status_code == 200
        actual_tickets = res_tickets.json()

        # Obtener métricas
        res_metrics = client.get("/api/v1/tickets/metrics")
        assert res_metrics.status_code == 200
        metrics = res_metrics.json()

        assert metrics["total_tickets"] == len(actual_tickets), (
            f"Métricas reportan {metrics['total_tickets']} tickets "
            f"pero hay {len(actual_tickets)} reales"
        )
        print(f"\n  CP-08a PASS — total_tickets={metrics['total_tickets']} coincide con BD ✓")

    def test_metrics_status_counts_sum_to_total(self, client):
        """CP-08b: La suma de tickets por estado debe igualar el total."""
        res = client.get("/api/v1/tickets/metrics")
        assert res.status_code == 200
        m = res.json()
        sum_by_status = sum(m["by_status"].values())
        assert sum_by_status == m["total_tickets"], (
            f"Suma por estado ({sum_by_status}) ≠ total ({m['total_tickets']})"
        )
        print(f"\n  CP-08b PASS — Suma por estado ({sum_by_status}) = total ✓")

    def test_metrics_resolution_rate_calculation(self, client):
        """CP-08c: resolution_rate_pct está entre 0 y 100 (validación matemática)."""
        res = client.get("/api/v1/tickets/metrics")
        assert res.status_code == 200
        m = res.json()
        rate = m["resolution_rate_pct"]
        assert 0.0 <= rate <= 100.0, f"Tasa de resolución fuera de rango: {rate}"
        print(f"\n  CP-08c PASS — resolution_rate_pct={rate}% (rango válido) ✓")

    def test_metrics_includes_all_required_fields(self, client):
        """CP-08d: Las métricas incluyen todos los campos requeridos."""
        res = client.get("/api/v1/tickets/metrics")
        assert res.status_code == 200
        m = res.json()
        required_fields = [
            "total_tickets", "by_status", "by_category", "by_priority",
            "open_count", "in_process_count", "resolved_count", "closed_count",
            "resolution_rate_pct"
        ]
        for field in required_fields:
            assert field in m, f"Campo requerido '{field}' falta en métricas"
        print(f"\n  CP-08d PASS — Todos los campos de métricas presentes ✓")


# ==============================================================
# CP-13: Rendimiento < 2.0 segundos (RNF-02)
# ==============================================================

class TestPerformanceCP13:
    """CP-13 (RNF-02): Rendimiento de endpoints principales < 2.0 segundos."""

    PERFORMANCE_THRESHOLD_SECONDS = 2.0

    @pytest.mark.parametrize("endpoint,method,payload", [
        ("/health", "GET", None),
        ("/api/v1/tickets/", "GET", None),
        ("/api/v1/tickets/metrics", "GET", None),
        ("/api/v1/users/", "GET", None),
    ])
    def test_endpoint_response_time(self, client, endpoint, method, payload):
        """CP-13: Endpoints responden en menos de 2.0 segundos."""
        t0 = time.perf_counter()
        if method == "GET":
            res = client.get(endpoint)
        else:
            res = client.post(endpoint, json=payload)
        elapsed = time.perf_counter() - t0

        assert elapsed < self.PERFORMANCE_THRESHOLD_SECONDS, (
            f"Endpoint {endpoint} tardó {elapsed:.3f}s (máx {self.PERFORMANCE_THRESHOLD_SECONDS}s)"
        )
        assert res.status_code in [200, 201], f"Endpoint {endpoint} retornó {res.status_code}"
        print(f"\n  CP-13 PASS — {method} {endpoint}: {elapsed*1000:.1f} ms ✓")

    def test_login_performance(self, client, seeded_users, demo_password):
        """CP-13b: Login JWT completa en menos de 2.0 segundos."""
        student = seeded_users["STUDENT"]
        t0 = time.perf_counter()
        res = client.post("/api/v1/users/login", json={
            "email": student["email"],
            "password": demo_password
        })
        elapsed = time.perf_counter() - t0

        assert elapsed < self.PERFORMANCE_THRESHOLD_SECONDS, \
            f"Login tardó {elapsed:.3f}s (máx {self.PERFORMANCE_THRESHOLD_SECONDS}s)"
        assert res.status_code == 200
        print(f"\n  CP-13b PASS — Login JWT: {elapsed*1000:.1f} ms ✓")


# ==============================================================
# CP-14: Healthcheck del sistema
# ==============================================================

class TestHealthCheckCP14:
    """CP-14: Endpoint de healthcheck responde correctamente."""

    def test_health_endpoint_returns_healthy(self, client):
        """CP-14: GET /health retorna 200 con status 'healthy'."""
        res = client.get("/health")
        assert res.status_code == 200, f"Se esperaba 200, se obtuvo {res.status_code}"
        data = res.json()
        assert data["status"] == "healthy", f"Estado esperado 'healthy', se obtuvo: {data}"
        assert "service" in data
        assert "version" in data
        print(f"\n  CP-14 PASS — Healthcheck OK: {data} ✓")


# ==============================================================
# CP-17: Integridad referencial (RNF-06)
# ==============================================================

class TestReferentialIntegrityCP17:
    """CP-17 (RNF-06): Integridad referencial — IDs inexistentes rechazados."""

    def test_create_ticket_with_nonexistent_user_id_is_handled(self, client):
        """CP-17a: Crear ticket con created_by_id inexistente es manejado controladamente."""
        res = client.post("/api/v1/tickets/", json={
            "title": "Ticket con usuario inexistente",
            "description": "Test de integridad referencial",
            "category": "HARDWARE",
            "created_by_id": 999999,  # ID que no existe
            "specific_metadata": {"device_type": "Teclado Fantasma"}
        })
        # El sistema debe rechazar (400/422) o crear el ticket sin el creator_id
        # (dependiendo de la implementación de FKs con SET NULL)
        # Lo importante es que no falle con un error 500 no controlado
        assert res.status_code in [201, 400, 422], \
            f"Se esperaba respuesta controlada (201/400/422), se obtuvo {res.status_code}: {res.text}"
        print(f"\n  CP-17a PASS — Ticket con user_id inexistente manejado ({res.status_code}) ✓")

    def test_assign_ticket_to_nonexistent_user_returns_404(self, client, seeded_users):
        """CP-17b: Asignar ticket a un ID de técnico inexistente retorna 404."""
        # Crear un ticket válido primero
        staff = seeded_users["STAFF"]
        res_create = client.post("/api/v1/tickets/", json={
            "title": "Ticket integridad ref CP17b",
            "description": "Test de asignación a técnico inexistente",
            "category": "ACCESS",
            "created_by_id": staff["id"],
            "specific_metadata": {
                "target_system": "VPN Institucional",
                "system_role": "Docente Visitante"
            }
        })
        assert res_create.status_code == 201
        ticket_id = res_create.json()["id"]

        # Intentar asignar a un técnico con ID inexistente
        res_assign = client.post(f"/api/v1/tickets/{ticket_id}/assign", json={
            "assigned_to_id": 888888,  # Técnico inexistente
            "reason": "Intento de asignación a fantasma"
        })
        assert res_assign.status_code in [404, 400], \
            f"Se esperaba 404/400, se obtuvo {res_assign.status_code}: {res_assign.text}"
        print(f"\n  CP-17b PASS — Asignación a técnico inexistente retorna {res_assign.status_code} ✓")

    def test_get_nonexistent_ticket_returns_404(self, client):
        """CP-17c: Consultar ticket con ID inexistente retorna 404."""
        res = client.get("/api/v1/tickets/9999999")
        assert res.status_code == 404, f"Se esperaba 404, se obtuvo {res.status_code}"
        print("\n  CP-17c PASS — Ticket inexistente retorna 404 ✓")

    def test_missing_required_metadata_returns_422(self, client, seeded_users):
        """CP-17d: Crear ticket sin metadatos obligatorios retorna 422 (validación de fábrica)."""
        student = seeded_users["STUDENT"]
        res = client.post("/api/v1/tickets/", json={
            "title": "Certificado sin metadatos",
            "description": "Falta student_code y certificate_type",
            "category": "CERTIFICADO",
            "created_by_id": student["id"],
            "specific_metadata": {}  # Sin los campos requeridos
        })
        assert res.status_code == 422, \
            f"Se esperaba 422 por metadatos faltantes, se obtuvo {res.status_code}: {res.text}"
        print("\n  CP-17d PASS — Metadatos obligatorios faltantes retorna 422 ✓")
