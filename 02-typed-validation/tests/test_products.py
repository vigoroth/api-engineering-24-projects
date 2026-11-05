from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

KNOWN_ID = "3f2b8c1e-7a4d-4e9b-9c6f-1d2e3a4b5c6d"


def test_t04_malformed_product_id_is_rejected():
    response = client.get("/products/not-a-uuid")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "product_id"]


def test_known_product_is_returned():
    response = client.get(f"/products/{KNOWN_ID}")
    assert response.status_code == 200
    assert response.json() == {"id": KNOWN_ID, "name": "Notebook"}


def test_unknown_but_valid_product_id_is_404():
    response = client.get("/products/00000000-0000-4000-8000-000000000000")
    assert response.status_code == 404




SECRET = "canary-supplier-password-7d1f"


def test_t06_internal_field_exists_in_storage():
    from app.main import PRODUCTS
    from uuid import UUID

    stored = PRODUCTS[UUID(KNOWN_ID)]
    assert stored.supplier_password == SECRET


def test_t06_internal_field_is_absent_from_public_response():
    response = client.get(f"/products/{KNOWN_ID}")
    assert response.status_code == 200
    assert "supplier_password" not in response.json()
    assert SECRET not in response.text
    assert SECRET not in str(response.headers)
