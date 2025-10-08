# from flask import Flask, render_template, request, jsonify
# import json, os

# app = Flask(__name__)

# # ===== JSONファイルのパス =====
# DATA_FILE = "data.json"

# # ===== ユーティリティ関数 =====
# def load_data():
#     """JSONファイルを読み込んでリストを返す。idがないレコードは補正して付与。"""
#     if not os.path.exists(DATA_FILE):   # ファイルが無ければ空リスト
#         return []
#     with open(DATA_FILE, "r", encoding="utf-8") as f:
#         try:
#             users = json.load(f)
#         except json.JSONDecodeError:
#             users = []   # ファイルが壊れていても安全に戻す

#     # --- ここで id を補正 ---
#     changed = False

#     # 既存の最大IDを取得（idがないレコードがあってもOK）
#     current_max = max((u.get("id", 0) for u in users), default=0)
#     next_id = current_max + 1

#     for u in users:
#         if "id" not in u :
#             u["id"] = next_id
#             next_id += 1
#             changed = True

#     # 補正が入ったら保存して永続化（次回移行もOK）   
#     if changed:
#         save_data(users)
#     return users
        
# def save_data(data):
#     """リストをJSONファイルに書き込む"""
#     with open(DATA_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)

# # ---------- HTML表示 ----------
# @app.route("/")
# def index():
#     return render_template("index.html")

# # ---------- データ受信 ----------
# @app.route("/api/register", methods=["POST"])
# def register():
#     data = request.get_json()   # JSから送られたJSONデータを受け取る
#     name = data.get("name")
#     email =data.get("email")

#     if not name or not email:
#         return jsonify({"status": "error", "message": "名前とメールは必須です。"}),400
    
#     users = load_data()

#     # 同じメールが既に存在していたらエラー
#     if any(u["email"] == email for u in users):
#         return jsonify({"status": "error", "message": "このメールはすでに登録済みです。"}),409
    
#     # 登録する情報に自動的にIDを付与する（番号管理）
#     new_id = max((u.get("id", 0) for u in users), default=0) + 1

#     # 新しいユーザーを追加
#     users.append({"id": new_id, "name": name, "email": email})
#     save_data(users)
#     return jsonify({"status": "success", "message": f"{name} さんを登録しました！"})

# # ===== 一覧取得API（GET） =====
# @app.route("/api/list", methods=["GET"])
# def get_list():
#     users = load_data()
#     return jsonify(users)

# # ===== 編集（Update） =====
# @app.route("/api/update/<int:user_id>", methods=["PUT"])
# def update_user(user_id):
#     data = request.get_json()
#     name = data.get("name")
#     email = data.get("email")

#     if not name or not email:
#         return jsonify({"status": "error", "message": "名前とメールは必須です。"}), 400

#     users = load_data()

#     # ★ 自分以外とのメール重複チェック（任意だが推奨）
#     if any(u.get("email") == email and u.get("id") != user_id for u in users):
#         return jsonify({"status": "error", "message": "このメールは別ユーザーで使用されています。"}), 409

#     for user in users:
#         if user.get("id") == user_id:   # get で安全比較
#             user["name"] = name
#             user["email"] = email
#             save_data(users)
#             return jsonify({"status": "success", "message": "更新しました。"})
#     return jsonify({"status": "error", "message": "該当ユーザーが見つかりません。"}), 404

# # ===== 削除（Delete） =====
# @app.route("/api/delete/<int:user_id>", methods=["DELETE"])
# def delete_user(user_id):
#     users = load_data()
#     new_users = [u for u in users if u.get("id") != user_id]

#     if len(new_users) == len(users):
#         return jsonify({"status": "error", "message": "該当ユーザーが見つかりませんでした。"}), 404
    
#     save_data(new_users)
#     return jsonify({"status": "success", "message": "削除しました。"})

# if __name__ == "__main__":
#     app.run(debug=True, host="127.0.0.1", port=8000)

# ↓＝＝＝＝＝DB（SQLite）バージョン ＝＝＝＝＝↓

from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# ===== learning/ を公開（学習用ページをブラウザ経由で開くため） =====
@app.route("/learning/<path:filename>")
def learning_static(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))   # .../flask_js_demo
    learning_dir = os.path.join(base_dir, "..", "learning") # .../learning
    return send_from_directory(learning_dir, filename)

# ===== データベース設定（app.py と同じフォルダの users.db を常に使う） =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "users.db")

def init_db():
    """データベースがなければ作成し、テーブルを準備"""
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                )
            """)
            conn.commit()

def get_connection():
    """毎回新しい接続を返す"""
    return sqlite3.connect(DB_FILE)

# ---------- HTML表示 ----------
@app.route("/")
def index():
    return render_template("index.html")

# ---------- 登録（Create） ----------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"status": "error", "message": "名前とメールは必須です。"}), 400

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
        return jsonify({"status": "success", "message": f"{name} さんを登録しました！"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "このアドレスはすでに登録済みです。"}), 409

# ---------- 一覧取得（Read） ----------
@app.route("/api/list", methods=["GET"])
def get_list():
    q = request.args.get("q", "", type=str).strip()
    sort = request.args.get("sort", "id_desc", type=str)

    where_sql = ""
    params = []
    if q:
        where_sql = "WHERE name LIKE ? OR email LIKE ?"
        like = f"%{q}%"
        params.extend([like, like])

    sort_map = {
        "id_asc": "id ASC",
        "id_desc": "id DESC",
        "name_asc": "name ASC",
        "name_desc": "name DESC",
        "email_asc": "email ASC",
        "email_desc": "email DESC",
    }
    order_by = sort_map.get(sort, "id DESC")

    sql = f"SELECT id, name, email FROM users {where_sql} ORDER BY {order_by}"

    with get_connection() as conn:
        c = conn.cursor()
        c.execute(sql, params)
        rows = c.fetchall()  # ← 一度だけ取得
        users = [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]

    return jsonify(users)

# ---------- 編集（Update） ----------
@app.route("/api/update/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"status": "error", "message": "名前とメールは必須です。"}), 400

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET name=?, email=? WHERE id=?", (name, email, user_id))
        conn.commit()
        if c.rowcount == 0:
            return jsonify({"status": "error", "message": "該当ユーザーが見つかりません。"}), 404

    return jsonify({"status": "success", "message": "更新しました。"})

# ---------- 削除（Delete） ----------
@app.route("/api/delete/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        if c.rowcount == 0:
            return jsonify({"status": "error", "message": "該当ユーザーが見つかりません。"}), 404

    return jsonify({"status": "success", "message": "削除しました。"})

# ---------- アプリ起動 ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=8000)