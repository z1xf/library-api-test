import pytest, requests
from conftest import BASE_URL

@pytest.mark.parametrize("username,expected_status", [
    ("ab", 400),       # 下边界外
    ("abc", 201),      # 下边界
    ("a"*20, 201),     # 上边界
    ("a"*21, 400),     # 上边界外
])
def test_register_username_boundary(username, expected_status):
    payload = {"username": username, "email": f"{username}@test.com", "password": "test123"}
    res = requests.post(f"{BASE_URL}/api/register", json=payload)
    assert res.status_code == expected_status

def test_login_wrong_password(registered_user):
    res = requests.post(f"{BASE_URL}/api/login", json={
        "username": registered_user["username"], "password": "wrong_pw"
    })
    assert res.status_code == 401
    assert "error" in res.json()