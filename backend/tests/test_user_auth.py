import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient

from backend.core.database import DatabaseManager


def main() -> None:
    DatabaseManager.reset_instance_for_testing()
    database = DatabaseManager("sqlite:///:memory:")
    database.create_all_tables()

    from backend.main import app

    with TestClient(app) as client:
        users_response = client.get("/api/v1/users/")
        assert users_response.status_code == 200, users_response.text
        assert len(users_response.json()) == 5

        create_response = client.post(
            "/api/v1/users/",
            json={
                "email": "prueba.auth@universidad.edu.co",
                "full_name": "Prueba de Autenticación",
                "role": "STUDENT",
                "password": "clave-personalizada",
            },
        )
        assert create_response.status_code == 201, create_response.text
        assert "password" not in create_response.json()

        valid_login = client.post(
            "/api/v1/users/login",
            json={
                "email": "prueba.auth@universidad.edu.co",
                "password": "clave-personalizada",
            },
        )
        assert valid_login.status_code == 200, valid_login.text

        invalid_login = client.post(
            "/api/v1/users/login",
            json={
                "email": "prueba.auth@universidad.edu.co",
                "password": "otra-clave",
            },
        )
        assert invalid_login.status_code == 401, invalid_login.text

        demo_login = client.post(
            "/api/v1/users/login",
            json={"email": "estudiante.camilo@universidad.edu.co"},
        )
        assert demo_login.status_code == 200, demo_login.text

        session = database.session_factory()
        try:
            from backend.domain.models.user import UserModel

            user = (
                session.query(UserModel)
                .filter_by(email="profesora.helena@universidad.edu.co")
                .first()
            )
            assert user is not None
            session.delete(user)
            session.commit()
        finally:
            session.close()

        reseed_response = client.post("/api/v1/users/seed")
        assert reseed_response.status_code == 200, reseed_response.text
        assert len(reseed_response.json()) == 6

    print("User creation and login tests passed.")


if __name__ == "__main__":
    main()
