"""
Authentication and Role-Based Access Control Tests.
"""

def test_register_customer_success(client, db_session):
    payload = {
        "username": "kofi_boateng",
        "email": "kofi@example.com",
        "phone_number": "0245556677",
        "password": "Password2026!",
        "full_name": "Kofi Boateng",
        "momo_network": "MTN",
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert "access_token" in data
    assert data["user"]["username"] == "kofi_boateng"
    assert data["user"]["phone_number"] == "0245556677"


def test_register_invalid_ghana_phone(client, db_session):
    payload = {
        "username": "invalid_user",
        "email": "invalid@example.com",
        "phone_number": "12345",  # Invalid format
        "password": "Password2026!",
        "full_name": "Invalid User",
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 400
    assert "Invalid Ghanaian phone number" in resp.get_json()["error"]


def test_login_success(client, db_session):
    # Register first
    client.post("/api/auth/register", json={
        "username": "yaadanso",
        "email": "yaa@example.com",
        "phone_number": "0541122334",
        "password": "SecretPassword1!",
        "full_name": "Yaa Danso",
    })

    # Login with phone
    resp = client.post("/api/auth/login", json={
        "login": "0541122334",
        "password": "SecretPassword1!",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data
    assert data["user"]["username"] == "yaadanso"


def test_login_invalid_password(client, db_session):
    resp = client.post("/api/auth/login", json={
        "login": "yaadanso",
        "password": "WrongPassword!",
    })
    assert resp.status_code == 401


def test_rbac_admin_only_endpoint(client, customer_headers, admin_headers):
    # Customer should be denied access to admin dashboard
    cust_resp = client.get("/api/admin/dashboard", headers=customer_headers)
    assert cust_resp.status_code == 403
    assert "Insufficient permissions" in cust_resp.get_json()["error"]

    # Admin should be permitted
    admin_resp = client.get("/api/admin/dashboard", headers=admin_headers)
    assert admin_resp.status_code == 200
