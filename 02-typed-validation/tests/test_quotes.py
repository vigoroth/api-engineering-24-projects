from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_t01_total_uses_decimal_arithemetic():

    response = client.post("/quotes", json={"unit_price": "0.10", "quantity": 3})
    assert response.status_code == 200
    assert response.json() == {"total": "0.30"}

def test_t02_zero_quantity_is_rejected():
    response = client.post("/quotes", json={"unit_price": "0.10", "quantity": 0})
    assert response.status_code == 422


def test_r02_absent_quantity_is_reported_as_missing():
    response = client.post("/quotes", json={"unit_price": "0.10"})
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == "missing"
    assert error["loc"] == ["body", "quantity"]


def test_r02_null_quantity_is_rejected_not_treated_as_absent():
    response = client.post("/quotes", json={"unit_price": "0.10", "quantity": None})
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == "int_type"
    assert error["loc"] == ["body", "quantity"]




def test_t03_non_integral_quantity_is_rejected():
    response = client.post("/quotes", json={"unit_price": "0.10", "quantity": 2.5})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "quantity"]


def test_r03_quantity_as_string_is_rejected():
    response = client.post("/quotes", json={"unit_price": "0.10", "quantity": "3"})
    assert response.status_code == 422


def test_r03_quantity_as_whole_float_is_rejected():
    response = client.post("/quotes", json={"unit_price": "0.10", "quantity": 3.0})
    assert response.status_code == 422


def test_r03_rounding_is_half_up():
    response = client.post("/quotes", json={"unit_price": "0.125", "quantity": 1})
    assert response.json() == {"total": "0.13"}




def test_r04_quantity_upper_bound_is_inclusive():
    response = client.post("/quotes", json={"unit_price": "0.10", "quantity": 1000})
    assert response.status_code == 200


def test_r04_quantity_above_upper_bound_is_rejected():
    response = client.post("/quotes", json={"unit_price": "0.10", "quantity": 1001})
    assert response.status_code == 422


def test_r04_zero_price_is_allowed():
    response = client.post("/quotes", json={"unit_price": "0", "quantity": 1})
    assert response.json() == {"total": "0.00"}


def test_r04_negative_price_is_rejected():
    response = client.post("/quotes", json={"unit_price": "-0.01", "quantity": 1})
    assert response.status_code == 422


def test_r04_huge_price_is_rejected_not_a_server_error():
    response = client.post("/quotes", json={"unit_price": "1e100", "quantity": 1})
    assert response.status_code == 422


def test_r04_too_many_decimal_places_is_rejected():
    response = client.post("/quotes", json={"unit_price": "0.12345", "quantity": 1})
    assert response.status_code == 422




def test_t05_missing_price_reports_field_location():
    response = client.post("/quotes", json={"quantity": 3})
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == "missing"
    assert error["loc"] == ["body", "unit_price"]


def test_r05_unknown_field_is_rejected():
    response = client.post(
        "/quotes", json={"unit_price": "0.10", "quantity": 3, "discount": "0.5"}
    )
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == "extra_forbidden"
    assert error["loc"] == ["body", "discount"]


def test_r05_misspelled_field_reports_both_problems():
    response = client.post("/quotes", json={"units_price": "0.10", "quantity": 3})
    assert response.status_code == 422
    problems = {(e["type"], tuple(e["loc"])) for e in response.json()["detail"]}
    assert problems == {
        ("missing", ("body", "unit_price")),
        ("extra_forbidden", ("body", "units_price")),
    }
