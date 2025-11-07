"""AWS Lambda handler to manage users in the app_user table."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import bcrypt
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

DEFAULT_HEADERS = {
    "Access-Control-Allow-Origin": os.getenv("CORS_ORIGIN", "*"),
    "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Content-Type": "application/json",
}


def _build_conninfo() -> str:
    host = os.getenv("PGHOST")
    dbname = os.getenv("PGDATABASE")
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    port = os.getenv("PGPORT", "5432")

    missing = [key for key, value in {
        "PGHOST": host,
        "PGDATABASE": dbname,
        "PGUSER": user,
        "PGPASSWORD": password,
    }.items() if not value]

    if missing:
        raise EnvironmentError(f"Missing database environment variables: {', '.join(missing)}")

    sslmode = os.getenv("PGSSLMODE")

    conninfo_parts = [
        f"host={host}",
        f"port={port}",
        f"dbname={dbname}",
        f"user={user}",
        f"password={password}",
    ]

    if sslmode:
        conninfo_parts.append(f"sslmode={sslmode}")

    return " ".join(conninfo_parts)


CONNECTION_POOL = ConnectionPool(
    conninfo=_build_conninfo(),
    min_size=1,
    max_size=int(os.getenv("PGPOOL_MAX", "4")),
    timeout=int(os.getenv("PGPOOL_TIMEOUT", "30")),
)


def _response(status_code: int, payload: Any) -> Dict[str, Any]:
    body = payload if isinstance(payload, str) else json.dumps(payload)
    return {
        "statusCode": status_code,
        "headers": DEFAULT_HEADERS,
        "body": body,
    }


def _parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    raw_body = event.get("body")
    if not raw_body:
        return {}

    try:
        return json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError as exc:  # pragma: no cover - lambda environment
        raise ValueError("Invalid JSON payload") from exc


def _get_user_identifier(path: str) -> Optional[str]:
    segments = [segment for segment in path.split("/") if segment]
    if len(segments) < 2:
        return None
    return segments[-1]


@dataclass
class User:
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "User":
        return cls(
            id=row["id"],
            email=row["email"],
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            is_active=row["is_active"],
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "isActive": self.is_active,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


def register_user(payload: Dict[str, Any]):
    email = payload.get("email")
    password = payload.get("password")
    first_name = payload.get("firstName")
    last_name = payload.get("lastName")

    if not email or not password:
        return _response(400, {"message": "Email y contraseña son obligatorios"})

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with CONNECTION_POOL.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT id FROM app_user WHERE email = %s", (email,))
            if cur.fetchone():
                return _response(409, {"message": "El usuario ya existe"})

            cur.execute(
                """
                INSERT INTO app_user (email, password_hash, first_name, last_name, is_active)
                VALUES (%s, %s, %s, %s, FALSE)
                RETURNING id, email, first_name, last_name, is_active, created_at, updated_at
                """,
                (email, hashed, first_name, last_name),
            )
            user_row = cur.fetchone()
            conn.commit()

    user = User.from_row(user_row)
    return _response(201, {"message": "Usuario registrado. Pendiente de activación", "user": user.as_dict()})


def login_user(payload: Dict[str, Any]):
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        return _response(400, {"message": "Credenciales incompletas"})

    with CONNECTION_POOL.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, email, password_hash, first_name, last_name, is_active, created_at, updated_at
                FROM app_user
                WHERE email = %s
                """,
                (email,),
            )
            row = cur.fetchone()

    if not row:
        return _response(401, {"message": "Usuario o contraseña inválidos"})

    if not row["is_active"]:
        return _response(403, {"message": "Usuario pendiente de activación"})

    if not bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
        return _response(401, {"message": "Usuario o contraseña inválidos"})

    user = User.from_row(row)
    return _response(200, {"message": "Inicio de sesión exitoso", "user": user.as_dict()})


def get_user(user_id: Optional[str]):
    if not user_id:
        return _response(400, {"message": "Se requiere el id del usuario"})

    with CONNECTION_POOL.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, email, first_name, last_name, is_active, created_at, updated_at
                FROM app_user
                WHERE id = %s
                """,
                (user_id,),
            )
            row = cur.fetchone()

    if not row:
        return _response(404, {"message": "Usuario no encontrado"})

    return _response(200, {"user": User.from_row(row).as_dict()})


def update_user(user_id: Optional[str], payload: Dict[str, Any]):
    if not user_id:
        return _response(400, {"message": "Se requiere el id del usuario"})

    updates = []
    values = []

    if "firstName" in payload:
        updates.append("first_name = %s")
        values.append(payload.get("firstName"))

    if "lastName" in payload:
        updates.append("last_name = %s")
        values.append(payload.get("lastName"))

    if "isActive" in payload:
        updates.append("is_active = %s")
        values.append(bool(payload.get("isActive")))

    if "password" in payload and payload.get("password"):
        hashed = bcrypt.hashpw(payload["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        updates.append("password_hash = %s")
        values.append(hashed)

    if not updates:
        return _response(400, {"message": "No hay campos para actualizar"})

    updates.append("updated_at = NOW()")

    with CONNECTION_POOL.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                UPDATE app_user
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, email, first_name, last_name, is_active, created_at, updated_at
                """,
                (*values, user_id),
            )
            row = cur.fetchone()
            conn.commit()

    if not row:
        return _response(404, {"message": "Usuario no encontrado"})

    return _response(200, {"message": "Usuario actualizado", "user": User.from_row(row).as_dict()})


def delete_user(user_id: Optional[str]):
    if not user_id:
        return _response(400, {"message": "Se requiere el id del usuario"})

    with CONNECTION_POOL.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM app_user WHERE id = %s", (user_id,))
            deleted = cur.rowcount
            conn.commit()

    if not deleted:
        return _response(404, {"message": "Usuario no encontrado"})

    return _response(204, "")


def handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    LOGGER.info("Incoming event: %s", json.dumps({k: event.get(k) for k in ("httpMethod", "path")}))

    if event.get("httpMethod") == "OPTIONS":
        return _response(200, {"ok": True})

    try:
        payload = _parse_body(event)
    except ValueError as exc:
        return _response(400, {"message": str(exc)})

    http_method = event.get("httpMethod", "GET")
    path = event.get("path", "/")

    if http_method == "POST" and path.endswith("/register"):
        return register_user(payload)

    if http_method == "POST" and path.endswith("/login"):
        return login_user(payload)

    if path.startswith("/users"):
        user_id = _get_user_identifier(path)

        if http_method == "GET":
            return get_user(user_id)

        if http_method in {"PUT", "PATCH"}:
            return update_user(user_id, payload)

        if http_method == "DELETE":
            return delete_user(user_id)

    return _response(
        404,
        {
            "message": "Ruta no encontrada",
            "hint": "Usa POST /register, POST /login o /users/{id}",
        },
    )


__all__ = ["handler"]

