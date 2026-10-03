import pytest, subprocess, time, requests, os
BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="session", autouse=True)
def start_server():
    db_path = os.path.join(os.path.dirname(__file__), "..", "app", "library.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    proc = subprocess.Popen(["python", "app/app.py"])
    time.sleep(1.5)  # 等待服务启动
    yield
    proc.terminate()

@pytest.fixture
def registered_user():
    import uuid
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {"username": username, "email": f"{username}@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/api/register", json=payload)
    return payload

@pytest.fixture
def auth_token(registered_user):
    res = requests.post(f"{BASE_URL}/api/login", json={
        "username": registered_user["username"],
        "password": registered_user["password"]
    })
    return res.json()["token"]