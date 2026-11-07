import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from backend.core.database import DatabaseManager

DatabaseManager.reset_instance_for_testing()
db = DatabaseManager("sqlite:///./unified_service_desk.db")
db.create_all_tables()

from backend.main import app

with TestClient(app) as client:
    # Check seeded users
    users = client.get("/api/v1/users/").json()
    print("Total users seeded:", len(users))
    for u in users:
        print(f" - {u['full_name']} ({u['role']}) -> {u['email']}")
    assert len(users) == 5

    # Check login
    login_res = client.post("/api/v1/users/login", json={"email": "estudiante.camilo@universidad.edu.co"})
    assert login_res.status_code == 200
    student = login_res.json()
    print("Login student OK:", student["full_name"])

    # Student creates a Certificate ticket
    cert_ticket = client.post("/api/v1/tickets/", json={
        "title": "Certificado de notas para beca",
        "description": "Requiero certificado de notas del semestre anterior con promedio acumulado",
        "category": "CERTIFICADO",
        "created_by_id": student["id"],
        "specific_metadata": {"student_code": "202210058", "certificate_type": "Certificado de Calificaciones"}
    }).json()
    print("Cert ticket created OK:", cert_ticket["id"], cert_ticket["category"], cert_ticket["priority"])

    # Staff creates a Hardware ticket
    staff_user = next(u for u in users if u["role"] == "STAFF")
    hw_ticket = client.post("/api/v1/tickets/", json={
        "title": "Proyector Aula 302 no enciende",
        "description": "El proyector no da imagen para la clase de las 4pm",
        "category": "HARDWARE",
        "created_by_id": staff_user["id"],
        "specific_metadata": {"device_type": "Proyector Epson", "serial_number": "PROY-AULA-302"}
    }).json()
    print("Hardware ticket created OK:", hw_ticket["id"], hw_ticket["category"])

    # IT Student Support takes student ticket
    it_student_user = next(u for u in users if u["role"] == "IT_STUDENT_SUPPORT")
    assign_res = client.post(f"/api/v1/tickets/{cert_ticket['id']}/assign", json={
        "assigned_to_id": it_student_user["id"],
        "reason": "Tomado por especialista de servicios estudiantiles"
    })
    assert assign_res.status_code == 200
    print("Assigned student ticket to IT student support OK!")

print("ALL UNIVERSITY TESTS PASSED 100%!")
