import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.core.database import DatabaseManager

DatabaseManager.reset_instance_for_testing()
db = DatabaseManager("sqlite:///:memory:")
db.create_all_tables()

from backend.main import app

with TestClient(app) as client:
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, res.text
    print("Health OK")

    # 2. Check seed users
    res = client.get("/api/v1/users/")
    assert res.status_code == 200, res.text
    users = res.json()
    assert len(users) >= 5, f"Expected >= 5 seed users, got {len(users)}"
    print(f"Users seeded successfully: {len(users)} users found")

    user_carlos = next(u for u in users if u["email"] == "carlos.gomez@empresa.com")
    tech_laura = next(u for u in users if u["email"] == "laura.ti@empresa.com")
    admin_andres = next(u for u in users if u["email"] == "andres.admin@empresa.com")
    assert user_carlos["role"] == "USER"
    assert tech_laura["role"] == "IT_SUPPORT"
    assert admin_andres["role"] == "ADMIN"
    print("Seed user roles verified:", user_carlos["full_name"], tech_laura["full_name"], admin_andres["full_name"])

    # 3. Create ticket as Carlos (Hardware)
    res = client.post("/api/v1/tickets/", json={
        "title": "Teclado derramado café",
        "description": "Se cayó líquido sobre el teclado y no funcionan teclas",
        "category": "HARDWARE",
        "created_by_id": user_carlos["id"],
        "specific_metadata": {"serial_number": "KB-CORP-991", "device_type": "Teclado Mecánico"}
    })
    assert res.status_code == 201, res.text
    t1 = res.json()
    ticket_id = t1["id"]
    assert t1["creator"]["full_name"] == "Carlos Gómez"
    assert t1["status"] == "OPEN"
    assert t1["assigned_to_id"] is None
    print("Ticket created with creator OK:", ticket_id, t1["creator"]["full_name"])

    # 4. Verify unassigned filter
    res = client.get("/api/v1/tickets/?unassigned=true")
    assert res.status_code == 200
    assert any(t["id"] == ticket_id for t in res.json())
    print("Unassigned filter OK")

    # 5. Try to assign ticket to a regular USER (Carlos) -> Should fail with 403 Forbidden!
    res = client.post(f"/api/v1/tickets/{ticket_id}/assign", json={
        "assigned_to_id": user_carlos["id"],
        "reason": "Intento ilegal de asignar a usuario normal"
    })
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
    print("RBAC check passed: cannot assign ticket to regular USER (403 Forbidden)")

    # 6. Assign ticket to Laura (IT_SUPPORT) -> Should succeed and auto-transition to IN_PROCESS!
    res = client.post(f"/api/v1/tickets/{ticket_id}/assign", json={
        "assigned_to_id": tech_laura["id"],
        "reason": "Asignado a Laura para cambio de periférico"
    })
    assert res.status_code == 200, res.text
    t1_assigned = res.json()
    assert t1_assigned["assigned_to_id"] == tech_laura["id"]
    assert t1_assigned["assignee"]["full_name"] == "Laura Técnico"
    assert t1_assigned["status"] == "IN_PROCESS"
    print("Ticket assigned to IT technician OK, status is now IN_PROCESS")

    # 7. Check user filter: Carlos should see his ticket
    res = client.get(f"/api/v1/tickets/?created_by_id={user_carlos['id']}")
    assert res.status_code == 200
    assert len(res.json()) >= 1
    print("Filter by created_by_id OK")

    # 8. Check assignee filter: Laura should see the ticket assigned to her
    res = client.get(f"/api/v1/tickets/?assigned_to_id={tech_laura['id']}")
    assert res.status_code == 200
    assert len(res.json()) >= 1
    print("Filter by assigned_to_id OK")

    # 9. Verify regular user (Carlos) cannot transition to RESOLVED directly (only IT/Admin can)
    res = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
        "target_status": "RESOLVED",
        "reason": "Carlos intentando resolver",
        "user_id": user_carlos["id"]
    })
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
    print("RBAC check passed: normal user cannot mark ticket as RESOLVED (403 Forbidden)")

    # 10. Technician Laura resolves ticket
    res = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
        "target_status": "RESOLVED",
        "reason": "Teclado reemplazado por stock nuevo",
        "user_id": tech_laura["id"]
    })
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "RESOLVED"
    print("Technician transition to RESOLVED OK")

    # 11. Check audit logs and notifications
    res = client.get(f"/api/v1/tickets/{ticket_id}/audit-logs")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) >= 3  # Creation + Assignment + Resolve
    print("Audit logs verified, total events:", len(logs))

    res = client.get("/api/v1/tickets/notifications/sent")
    assert res.status_code == 200
    emails = res.json()
    assert len(emails) >= 3
    print("Email notifications verified, total dispatched:", len(emails))

print("ALL BACKEND USER & ROLE RBAC TESTS PASSED 100%!")
