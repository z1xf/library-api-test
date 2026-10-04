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


@allure.epic("图书借阅管理系统")
@allure.feature("用户管理")
@allure.story("用户注册")
@allure.title("邮箱格式错误时注册应返回400")
def test_register_invalid_email():
    """TC-005: 邮箱格式错误，应返回400"""
    payload = {
        "username": "invalid_email_user",
        "email": "abc123",
        "password": "test123"
    }
    res = requests.post(f"{BASE_URL}/api/register", json=payload)
    assert res.status_code == 400


@allure.epic("图书借阅管理系统")
@allure.feature("用户管理")
@allure.story("用户注册")
@allure.title("密码长度不足时注册应返回400")
def test_register_password_too_short():
    """TC-006: 密码长度为5时，应返回400"""
    payload = {
        "username": "short_password_user",
        "email": "short_password@test.com",
        "password": "12345"
    }
    res = requests.post(f"{BASE_URL}/api/register", json=payload)
    assert res.status_code == 400


@allure.epic("图书借阅管理系统")
@allure.feature("用户管理")
@allure.story("用户注册")
@allure.title("用户名重复注册应返回409")
def test_register_duplicate_username(registered_user):
    """TC-007: 使用已存在的用户名重复注册，应返回409"""
    res = requests.post(f"{BASE_URL}/api/register", json=registered_user)
    assert res.status_code == 409