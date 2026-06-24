import requests, uuid
from conftest import BASE_URL

def _register_and_login():
    """辅助函数：注册一个新用户并登录，返回token。用于需要第二个用户身份的场景。"""
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(f"{BASE_URL}/api/register", json={
        "username": username, "email": f"{username}@test.com", "password": "test123"
    })
    res = requests.post(f"{BASE_URL}/api/login", json={"username": username, "password": "test123"})
    return res.json()["token"]

def test_history_requires_login():
    """TC-022: 未登录查询借阅历史，应返回401"""
    res = requests.get(f"{BASE_URL}/api/borrow/history")
    assert res.status_code == 401

def test_history_empty_for_new_user(auth_token):
    """TC-023: 新用户没有任何借阅记录，应返回空列表"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = requests.get(f"{BASE_URL}/api/borrow/history", headers=headers)
    assert res.status_code == 200
    assert res.json() == []

def test_history_data_isolation(auth_token):
    """TC-016: 用户A的借阅记录里不应出现用户B的数据"""
    headers_a = {"Authorization": f"Bearer {auth_token}"}
    requests.post(f"{BASE_URL}/api/books", json={"title": "数据隔离测试书", "stock": 2}, headers=headers_a)
    book_id = requests.get(f"{BASE_URL}/api/books", params={"title": "数据隔离测试书"}).json()[0]["id"]
    requests.post(f"{BASE_URL}/api/borrow", json={"book_id": book_id}, headers=headers_a)

    token_b = _register_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}
    history_b = requests.get(f"{BASE_URL}/api/borrow/history", headers=headers_b).json()
    assert history_b == [], "用户B不应该看到用户A的借阅记录"