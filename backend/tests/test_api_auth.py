from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def test_signup_login_me_flow() -> None:
    client = TestClient(app)
    r = client.post("/api/auth/signup", json={"email": "a@b.com", "password": "supersecret"})
    assert r.status_code == 201, r.text
    token = r.json()["access_token"]

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "a@b.com"

    r = client.post("/api/auth/login", json={"email": "a@b.com", "password": "supersecret"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_duplicate_signup_rejected() -> None:
    client = TestClient(app)
    body = {"email": "dup@b.com", "password": "supersecret"}
    assert client.post("/api/auth/signup", json=body).status_code == 201
    assert client.post("/api/auth/signup", json=body).status_code == 400
