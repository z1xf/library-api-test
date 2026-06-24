from flask import Flask, request, jsonify
import sqlite3, jwt, datetime, re
import os

app = Flask(__name__)
SECRET_KEY = "test_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_db():
    conn = sqlite3.connect(os.path.join(BASE_DIR, "library.db"))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE, email TEXT, password TEXT
    );
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, stock INTEGER
    );
    CREATE TABLE IF NOT EXISTS borrows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, book_id INTEGER, status TEXT
    );
    """)
    conn.commit()
    conn.close()

def get_user_id_from_token(req):
    token = req.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except Exception:
        return None

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "")
    email = data.get("email", "")
    password = data.get("password", "")

    if not (3 <= len(username) <= 20):
        return jsonify({"error": "用户名长度需在3-20位之间"}), 400
    if not re.match(r"^[\w.+-]+@[\w-]+\.[\w.-]+$", email):
        return jsonify({"error": "邮箱格式不正确"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码长度至少6位"}), 400

    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)",
                     (username, email, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "用户名已存在"}), 409
    finally:
        conn.close()
    return jsonify({"message": "注册成功"}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                        (data.get("username"), data.get("password"))).fetchone()
    conn.close()
    if not user:
        return jsonify({"error": "用户名或密码错误"}), 401
    token = jwt.encode({"user_id": user["id"],
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
                       SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token}), 200

@app.route("/api/books", methods=["POST"])
def add_book():
    if not get_user_id_from_token(request):
        return jsonify({"error": "未授权"}), 401
    data = request.get_json() or {}
    title = data.get("title")
    stock = data.get("stock", 0)
    if not title:
        return jsonify({"error": "图书名称不能为空"}), 400
    if not isinstance(stock, int) or stock < 0:
        return jsonify({"error": "库存数量不能为负数"}), 400
    conn = get_db()
    conn.execute("INSERT INTO books (title, stock) VALUES (?,?)", (data.get("title"), stock))
    conn.commit()
    conn.close()
    return jsonify({"message": "添加成功"}), 201

@app.route("/api/books", methods=["GET"])
def list_books():
    keyword = request.args.get("title", "")
    conn = get_db()
    rows = conn.execute("SELECT * FROM books WHERE title LIKE ?", (f"%{keyword}%",)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

@app.route("/api/borrow", methods=["POST"])
def borrow():
    user_id = get_user_id_from_token(request)
    if not user_id:
        return jsonify({"error": "未授权"}), 401
    book_id = (request.get_json() or {}).get("book_id")
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    if not book:
        conn.close()
        return jsonify({"error": "图书不存在"}), 404

    if book["stock"] <= 0:
        conn.close()
        return jsonify({"error": "库存不足"}), 400
    existing = conn.execute(
        "SELECT * FROM borrows WHERE user_id=? AND book_id=? AND status='borrowed'",
        (user_id, book_id)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "您已借阅此书，请先归还"}), 400
    conn.execute("UPDATE books SET stock = stock - 1 WHERE id=?", (book_id,))
    conn.execute("INSERT INTO borrows (user_id, book_id, status) VALUES (?,?,'borrowed')",
                (user_id, book_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "借阅成功"}), 200

@app.route("/api/return", methods=["POST"])
def return_book():
    user_id = get_user_id_from_token(request)
    if not user_id:
        return jsonify({"error": "未授权"}), 401
    book_id = (request.get_json() or {}).get("book_id")
    conn = get_db()
    record = conn.execute(
        "SELECT * FROM borrows WHERE user_id=? AND book_id=? AND status='borrowed'",
        (user_id, book_id)).fetchone()
    if not record:
        conn.close()
        return jsonify({"error": "没有找到对应的借阅记录"}), 400
    conn.execute("UPDATE borrows SET status='returned' WHERE id=?", (record["id"],))
    conn.execute("UPDATE books SET stock = stock + 1 WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "还书成功"}), 200

@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    conn.close()
    if not book:
        return jsonify({"error": "图书不存在"}), 404
    return jsonify(dict(book)), 200

@app.route("/api/borrow/history", methods=["GET"])
def borrow_history():
    user_id = get_user_id_from_token(request)
    if not user_id:
        return jsonify({"error": "未授权"}), 401
    conn = get_db()
    rows = conn.execute("SELECT * FROM borrows WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True, use_reloader=False, port=5000)
