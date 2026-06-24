import requests
from conftest import BASE_URL
def test_add_book_missing_title(auth_token):
    """TC-017: 新增图书时缺少title字段，应返回400"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = requests.post(f"{BASE_URL}/api/books", json={"stock": 5}, headers=headers)
    assert res.status_code == 400, (
        f"预期缺少title字段时返回400，实际返回 {res.status_code}"
    )

def test_add_book_invalid_stock_type(auth_token):
    """TC-018: stock传字符串而非数字，应返回400"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = requests.post(f"{BASE_URL}/api/books",
                        json={"title": "无效库存测试书", "stock": "abc"}, headers=headers)
    assert res.status_code == 400

def test_search_book_by_keyword(auth_token):
    """TC-019: 模糊搜索能查到包含关键字的书"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    requests.post(f"{BASE_URL}/api/books", json={"title": "计算机网络", "stock": 3}, headers=headers)
    res = requests.get(f"{BASE_URL}/api/books", params={"title": "计算机"})
    assert res.status_code == 200
    assert any("计算机" in b["title"] for b in res.json())

def test_search_book_no_match():
    """TC-020: 搜索不存在的关键字，应返回空列表"""
    res = requests.get(f"{BASE_URL}/api/books", params={"title": "xxxxx不存在的书名"})
    assert res.status_code == 200
    assert res.json() == []

def test_get_book_not_found():
    """TC-021: 查询不存在的图书id，应返回404"""
    res = requests.get(f"{BASE_URL}/api/books/999999")
    assert res.status_code == 404