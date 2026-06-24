import requests
from conftest import BASE_URL
def test_borrow_when_stock_is_zero(auth_token):
    """核心用例：库存为0时不应允许借阅。这条用例会暴露后端的边界判断bug。"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # 先建一本库存为0的书
    add_res = requests.post(f"{BASE_URL}/api/books", json={"title": "测试书籍", "stock": 0}, headers=headers)
    book_id = requests.get(f"{BASE_URL}/api/books", params={"title": "测试书籍"}).json()[0]["id"]

    borrow_res = requests.post(f"{BASE_URL}/api/borrow", json={"book_id": book_id}, headers=headers)

    assert borrow_res.status_code == 400, (
        f"预期库存为0时拒绝借阅(400)，实际返回 {borrow_res.status_code}，"
        f"说明库存边界判断存在缺陷"
    )

def test_borrow_and_return_flow(auth_token):
    """正常借还书完整流程"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    requests.post(f"{BASE_URL}/api/books", json={"title": "流程测试书", "stock": 1}, headers=headers)
    book_id = requests.get(f"{BASE_URL}/api/books", params={"title": "流程测试书"}).json()[0]["id"]

    borrow_res = requests.post(f"{BASE_URL}/api/borrow", json={"book_id": book_id}, headers=headers)
    assert borrow_res.status_code == 200

    return_res = requests.post(f"{BASE_URL}/api/return", json={"book_id": book_id}, headers=headers)
    assert return_res.status_code == 200

def test_duplicate_borrow_without_return(auth_token):
    """同一本书在未归还的情况下重复借阅应被拒绝"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    requests.post(f"{BASE_URL}/api/books", json={"title": "重复借阅测试书", "stock": 5}, headers=headers)
    book_id = requests.get(f"{BASE_URL}/api/books", params={"title": "重复借阅测试书"}).json()[0]["id"]

    requests.post(f"{BASE_URL}/api/borrow", json={"book_id": book_id}, headers=headers)
    second_res = requests.post(f"{BASE_URL}/api/borrow", json={"book_id": book_id}, headers=headers)
    assert second_res.status_code == 400

def test_return_book_borrowed_by_others(auth_token):
    """TC-024: 用户A不能归还用户B借阅的图书"""
    import uuid
    headers_a = {"Authorization": f"Bearer {auth_token}"}

    requests.post(f"{BASE_URL}/api/books", json={"title": "越权还书测试书", "stock": 1}, headers=headers_a)
    book_id = requests.get(f"{BASE_URL}/api/books", params={"title": "越权还书测试书"}).json()[0]["id"]
    requests.post(f"{BASE_URL}/api/borrow", json={"book_id": book_id}, headers=headers_a)

    # 注册另一个用户B，尝试还用户A借的这本书
    username_b = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(f"{BASE_URL}/api/register", json={
        "username": username_b, "email": f"{username_b}@test.com", "password": "test123"
    })
    login_res = requests.post(f"{BASE_URL}/api/login",
                              json={"username": username_b, "password": "test123"})
    token_b = login_res.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    return_res = requests.post(f"{BASE_URL}/api/return", json={"book_id": book_id}, headers=headers_b)
    assert return_res.status_code == 400, (
        f"预期用户B不能还用户A借的书(400)，实际返回 {return_res.status_code}"
    )