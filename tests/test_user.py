import pytest, requests, allure

from conftest import BASE_URL

@allure.epic("图书借阅管理系统")
@allure.feature("用户管理")
@allure.story("用户注册")
@allure.title("用户名长度边界校验")
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


@allure.epic("图书借阅管理系统")
@allure.feature("用户管理")
@allure.story("用户登录")
@allure.title("使用错误密码登录应返回401")
def test_login_wrong_password(registered_user):
    res = requests.post(f"{BASE_URL}/api/login", json={
        "username": registered_user["username"], "password": "wrong_pw"
    })
    assert res.status_code == 401
    assert "error" in res.json()