"""
test_user_auth.py — Pruebas de autenticación, hashing y JWT.

Cubre:
- CP-05 (RF-05): Login válido (200 + JWT) e inválido (401)
- CP-10 (RNF-01 / DEF-01): Hash Argon2id verificado en BD
- CP-11 (RNF-01 / DEF-03): Pruebas de seguridad JWT
- CP-12 (RNF-01 / DEF-02): Escaneo de credenciales hardcodeadas
"""

import os
import re
import sys
import time
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.tests.conftest import auth_headers


# ==============================================================
# CP-05: Login con credenciales válidas e inválidas
# ==============================================================

class TestLoginCP05:
    """CP-05 (RF-05): Autenticación con JWT."""

    def test_login_valid_returns_200_and_jwt(self, client, seeded_users, demo_password):
        """CP-05a: Login exitoso retorna 200 + access_token + user (sin password)."""
        student = seeded_users["STUDENT"]
        t0 = time.perf_counter()
        res = client.post("/api/v1/users/login", json={
            "email": student["email"],
            "password": demo_password
        })
        elapsed_ms = (time.perf_counter() - t0) * 1000

        assert res.status_code == 200, f"Se esperaba 200, se obtuvo {res.status_code}: {res.text}"
        data = res.json()
        assert "access_token" in data, "Falta access_token en la respuesta"
        assert data["token_type"] == "bearer", "token_type debe ser 'bearer'"
        assert "user" in data, "Falta objeto user en la respuesta"
        assert "password" not in data["user"], "La contraseña NO debe estar en la respuesta"
        assert data["user"]["role"] == "STUDENT"
        print(f"\n  CP-05a PASS — Login STUDENT OK ({elapsed_ms:.1f} ms)")

    def test_login_invalid_password_returns_401(self, client, seeded_users):
        """CP-05b: Login con contraseña incorrecta retorna 401."""
        student = seeded_users["STUDENT"]
        res = client.post("/api/v1/users/login", json={
            "email": student["email"],
            "password": "contraseña-incorrecta-99"
        })
        assert res.status_code == 401, f"Se esperaba 401, se obtuvo {res.status_code}"
        print("\n  CP-05b PASS — Login inválido retorna 401 ✓")

    def test_login_nonexistent_user_returns_401(self, client):
        """CP-05c: Email que no existe retorna 401 (no 404 — no revelar existencia)."""
        res = client.post("/api/v1/users/login", json={
            "email": "noexiste@universidad.edu.co",
            "password": "cualquiera"
        })
        assert res.status_code == 401, f"Se esperaba 401, se obtuvo {res.status_code}"
        print("\n  CP-05c PASS — Email inexistente retorna 401 ✓")

    def test_login_all_5_roles(self, client, seeded_users, demo_password):
        """CP-05d: Los 5 roles institucionales pueden iniciar sesión."""
        for role, user in seeded_users.items():
            res = client.post("/api/v1/users/login", json={
                "email": user["email"],
                "password": demo_password
            })
            assert res.status_code == 200, f"Login falló para rol {role}: {res.text}"
            token = res.json().get("access_token")
            assert token, f"No se recibió token para rol {role}"
        print("\n  CP-05d PASS — Los 5 roles pueden iniciar sesión ✓")

    def test_login_response_does_not_expose_password(self, client, seeded_users, demo_password):
        """CP-05e: La respuesta de login no expone contraseña en ningún nivel."""
        student = seeded_users["STUDENT"]
        res = client.post("/api/v1/users/login", json={
            "email": student["email"],
            "password": demo_password
        })
        assert res.status_code == 200
        response_text = res.text
        assert "password" not in response_text.lower() or '"password"' not in response_text, \
            "La respuesta no debe exponer el campo password"
        print("\n  CP-05e PASS — Contraseña no expuesta en respuesta ✓")


# ==============================================================
# CP-10: Hash Argon2id verificado en BD (DEF-01)
# ==============================================================

class TestPasswordHashCP10:
    """CP-10 (RNF-01 / DEF-01): Verificación de hash Argon2id en base de datos."""

    def test_password_stored_as_argon2id_hash(self, db, seeded_users, demo_password):
        """CP-10a: La contraseña almacenada en BD comienza con $argon2id$ y no es texto plano."""
        from backend.domain.models.user import UserModel

        session = db.session_factory()
        try:
            student_email = seeded_users["STUDENT"]["email"]
            user = session.query(UserModel).filter_by(email=student_email).first()
            assert user is not None, "Usuario STUDENT no encontrado en BD"
            assert user.password.startswith("$argon2id$"), \
                f"Hash debe comenzar con '$argon2id$', se encontró: {user.password[:20]}..."
            assert user.password != demo_password, \
                "La contraseña NO debe ser idéntica al texto plano"
            assert len(user.password) >= 60, \
                f"Hash demasiado corto para Argon2id: {len(user.password)} chars"
        finally:
            session.close()
        print("\n  CP-10a PASS — Contraseña almacenada como hash Argon2id ✓")

    def test_new_user_password_is_hashed(self, client, db):
        """CP-10b: Al crear un nuevo usuario, la contraseña se hashea antes de persistir."""
        from backend.domain.models.user import UserModel

        NEW_EMAIL = "hash.test.user@universidad.edu.co"
        NEW_PASS = "MiContraseñaSegura123"

        res = client.post("/api/v1/users/", json={
            "email": NEW_EMAIL,
            "full_name": "Usuario Test Hash",
            "role": "STUDENT",
            "password": NEW_PASS
        })
        assert res.status_code == 201, f"Creación de usuario falló: {res.text}"
        assert "password" not in res.json(), "La respuesta no debe exponer la contraseña"

        session = db.session_factory()
        try:
            user = session.query(UserModel).filter_by(email=NEW_EMAIL).first()
            assert user is not None
            assert user.password.startswith("$argon2id$"), \
                f"Nuevo usuario debe tener hash Argon2id, se encontró: {user.password[:20]}"
            assert user.password != NEW_PASS, "No debe almacenarse texto plano"
        finally:
            session.close()
        print("\n  CP-10b PASS — Nuevo usuario almacenado con hash Argon2id ✓")

    def test_hash_uniqueness_same_password(self, db, seeded_users):
        """CP-10c: Dos usuarios con la misma contraseña tienen hashes distintos (salt único)."""
        from backend.domain.models.user import UserModel

        session = db.session_factory()
        try:
            users = session.query(UserModel).limit(2).all()
            if len(users) >= 2:
                assert users[0].password != users[1].password, \
                    "Hashes deben ser únicos aunque la contraseña sea igual (salt distinto)"
        finally:
            session.close()
        print("\n  CP-10c PASS — Hashes únicos por usuario (salt aleatorio) ✓")


# ==============================================================
# CP-11: Seguridad JWT (DEF-03)
# ==============================================================

class TestJWTSecurityCP11:
    """CP-11 (RNF-01 / DEF-03): Pruebas de seguridad de tokens JWT."""

    def test_request_without_auth_header_still_works_on_public_endpoints(self, client):
        """CP-11a: Endpoints públicos (seed, listado) no requieren token."""
        res = client.get("/api/v1/users/")
        assert res.status_code == 200
        res_health = client.get("/health")
        assert res_health.status_code == 200
        print("\n  CP-11a PASS — Endpoints públicos accesibles sin token ✓")

    def test_me_endpoint_without_token_returns_401(self, client):
        """CP-11b: GET /me sin Authorization header retorna 401."""
        res = client.get("/api/v1/users/me")
        assert res.status_code == 401, f"Se esperaba 401, se obtuvo {res.status_code}"
        print("\n  CP-11b PASS — /me sin token retorna 401 ✓")

    def test_me_with_tampered_signature_returns_401(self, client, student_token):
        """CP-11c: JWT con firma alterada retorna 401."""
        # Alterar el último carácter del token (signature segment)
        tampered = student_token[:-4] + "XXXX"
        res = client.get("/api/v1/users/me", headers=auth_headers(tampered))
        assert res.status_code == 401, f"Se esperaba 401 con token manipulado, se obtuvo {res.status_code}"
        print("\n  CP-11c PASS — Token con firma alterada retorna 401 ✓")

    def test_me_with_expired_token_returns_401(self, client, seeded_users, demo_password):
        """CP-11d: JWT con exp ya vencido retorna 401."""
        from datetime import timedelta
        from backend.core.security import create_access_token

        student = seeded_users["STUDENT"]
        # Crear token con expiración negativa (ya expiró)
        expired_token = create_access_token(
            data={"sub": str(student["id"]), "role": student["role"]},
            expires_delta=timedelta(seconds=-1)
        )
        res = client.get("/api/v1/users/me", headers=auth_headers(expired_token))
        assert res.status_code == 401, f"Se esperaba 401 con token expirado, se obtuvo {res.status_code}"
        print("\n  CP-11d PASS — Token expirado retorna 401 ✓")

    def test_me_with_valid_token_returns_user(self, client, student_token, seeded_users):
        """CP-11e: JWT válido en /me retorna datos del usuario autenticado."""
        res = client.get("/api/v1/users/me", headers=auth_headers(student_token))
        assert res.status_code == 200, f"Se esperaba 200, se obtuvo {res.status_code}: {res.text}"
        data = res.json()
        assert data["role"] == "STUDENT"
        assert "password" not in data
        print("\n  CP-11e PASS — Token válido en /me retorna usuario ✓")

    def test_malformed_token_returns_401(self, client):
        """CP-11f: Token malformado (no es JWT) retorna 401."""
        res = client.get("/api/v1/users/me", headers={"Authorization": "Bearer notajwt.at.all"})
        assert res.status_code == 401
        print("\n  CP-11f PASS — Token malformado retorna 401 ✓")


# ==============================================================
# CP-12: Escaneo de credenciales hardcodeadas (DEF-02)
# ==============================================================

class TestNoHardcodedCredsCP12:
    """CP-12 (RNF-01 / DEF-02): Escaneo estático de contraseñas hardcodeadas."""

    PATTERNS_FORBIDDEN = [
        r'"12345"',
        r"'12345'",
        r"password\s*=\s*['\"]12345['\"]",
        r"DEFAULT\s+['\"]12345['\"]",
    ]

    EXTENSIONS_PYTHON = [".py"]
    EXTENSIONS_JS = [".js", ".jsx", ".ts", ".tsx"]

    def _scan_files(self, root: str, extensions: list) -> list:
        """Busca patrones prohibidos en archivos de código fuente (excluye archivos de test)."""
        violations = []
        for dirpath, dirnames, filenames in os.walk(root):
            # Ignorar cachés, node_modules y directorios de test (que contienen los patrones como strings de búsqueda)
            dirnames[:] = [
                d for d in dirnames
                if d not in {"__pycache__", "node_modules", ".git", "venv", ".venv", "dist", "tests"}
            ]
            for fname in filenames:
                if any(fname.endswith(ext) for ext in extensions):
                    # Excluir archivos de prueba — pueden contener patrones como strings de búsqueda
                    if fname.startswith("test_") or fname == "conftest.py":
                        continue
                    fpath = os.path.join(dirpath, fname)
                    try:
                        content = open(fpath, encoding="utf-8", errors="ignore").read()
                        for pattern in self.PATTERNS_FORBIDDEN:
                            if re.search(pattern, content, re.IGNORECASE):
                                violations.append((fpath, pattern))
                    except OSError:
                        pass
        return violations

    def test_no_hardcoded_password_in_python_files(self):
        """CP-12a: Ningún archivo .py contiene '12345' como contraseña literal."""
        backend_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        violations = self._scan_files(backend_root, self.EXTENSIONS_PYTHON)
        assert violations == [], (
            f"Contraseñas hardcodeadas encontradas en archivos Python:\n"
            + "\n".join(f"  {f}: patrón '{p}'" for f, p in violations)
        )
        print("\n  CP-12a PASS — Sin contraseñas hardcodeadas en archivos Python ✓")

    def test_no_hardcoded_password_in_js_files(self):
        """CP-12b: Ningún archivo .js/.jsx contiene '12345' como contraseña literal."""
        frontend_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../frontend/src")
        )
        if not os.path.isdir(frontend_root):
            pytest.skip("Directorio frontend/src no encontrado")
        violations = self._scan_files(frontend_root, self.EXTENSIONS_JS)
        assert violations == [], (
            f"Contraseñas hardcodeadas encontradas en archivos JS/JSX:\n"
            + "\n".join(f"  {f}: patrón '{p}'" for f, p in violations)
        )
        print("\n  CP-12b PASS — Sin contraseñas hardcodeadas en archivos JS/JSX ✓")
