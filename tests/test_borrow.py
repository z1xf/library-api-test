import requests, allure

from conftest import BASE_URL


@allure.epic("图书借阅管理系统")
@allure.feature("借阅管理")
@allure.story("库存边界")
@allure.title("库存为0时不应允许借阅")
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


@allure.epic("图书借阅管理系统")
@allure.feature("借阅管理")
@allure.story("正常借还流程")
@allure.title("用户完成借书后可以正常还书")
def test_borrow_and_return_flow(auth_token):
    """正常借还书完整流程"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    requests.post(f"{BASE_URL}/api/books", json={"title": "流程测试书", "stock": 1}, headers=headers)
    book_id = requests.get(f"{BASE_URL}/api/books", params={"title": "流程测试书"}).json()[0]["id"]

    borrow_res = requests.post(f"{BASE_URL}/api/borrow", json={"book_id": book_id}, headers=headers)
    assert borrow_res.status_code == 200

    return_res = requests.post(f"{BASE_URL}/api/return", json={"book_id": book_id}, headers=headers)
    assert return_res.status_code == 200


@allure.epic("图书借阅管理系统")
@allure.feature("借阅管理")
@allure.story("重复借阅")
@allure.title("同一本书未归还前重复借阅应被拒绝")
def test_duplicate_borrow_without_return(auth_token):
    """同一本书在未归还的情况下重复借阅应被拒绝"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    requests.post(f"{BASE_URL}/api/books", json={"title": "重复借阅测试书", "stock": 5}, headers=headers)
    book_id = requests.get(f"{BASE_URL}/api/books", params={"title": "重复借阅测试书"}).json()[0]["id"]

    requests.post(f"{BASE_URL}/api/borrow", json={"book_id": book_id}, headers=headers)
    second_res = requests.post(f"{BASE_URL}/api/borrow", json={"book_id": book_id}, headers=headers)
    assert second_res.status_code == 400


@allure.epic("图书借阅管理系统")
@allure.feature("借阅管理")
@allure.story("权限与数据隔离")
@allure.title("用户不能归还其他用户借阅的图书")
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


@allure.epic("图书借阅管理系统")
@allure.feature("借阅管理")
@allure.story("库存边界")
@allure.title("库存为1时借阅成功且库存变为0")
def test_borrow_when_stock_is_one(auth_token):
    """TC-010: 库存为1时借阅成功，借阅后库存应变为0"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    requests.post(f"{BASE_URL}/api/books",
                  json={"title": "库存为1测试书", "stock": 1},
                  headers=headers)
    book_id = requests.get(f"{BASE_URL}/api/books",
                           params={"title": "库存为1测试书"}).json()[0]["id"]

    borrow_res = requests.post(f"{BASE_URL}/api/borrow",
                               json={"book_id": book_id},
                               headers=headers)
    assert borrow_res.status_code == 200

    book_res = requests.get(f"{BASE_URL}/api/books/{book_id}")
    assert book_res.status_code == 200
    assert book_res.json()["stock"] == 0


@allure.epic("图书借阅管理系统")
@allure.feature("借阅管理")
@allure.story("异常场景")
@allure.title("借阅不存在的图书ID应返回404")
def test_borrow_book_not_found(auth_token):
    """TC-012: 借阅不存在的图书id，应返回404"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = requests.post(f"{BASE_URL}/api/borrow",
                        json={"book_id": 99999},
                        headers=headers)
    assert res.status_code == 404


@allure.epic("图书借阅管理系统")
@allure.feature("借阅管理")
@allure.story("身份认证")
@allure.title("未携带Token借阅应返回401")
def test_borrow_without_token():
    """TC-013: 未携带Authorization header借阅，应返回401"""
    res = requests.post(f"{BASE_URL}/api/borrow",
                        json={"book_id": 99999})
    assert res.status_code == 401


@allure.epic("图书借阅管理系统")
@allure.feature("借阅管理")
@allure.story("正常还书")
@allure.title("归还未借阅的图书应返回400")
def test_return_book_not_borrowed(auth_token):
    """TC-014: 用户未借阅该图书时直接还书，应返回400"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    requests.post(f"{BASE_URL}/api/books",
                  json={"title": "未借阅还书测试书", "stock": 1},
                  headers=headers)
    book_id = requests.get(f"{BASE_URL}/api/books",
                           params={"title": "未借阅还书测试书"}).json()[0]["id"]

    return_res = requests.post(f"{BASE_URL}/api/return",
                               json={"book_id": book_id},
                               headers=headers)
    assert return_res.status_code == 400