from flask import Flask, render_template, request, jsonify
import json, os

app = Flask(__name__)

# ===== JSONファイルのパス =====
DATA_FILE = "data.json"

# ===== ユーティリティ関数 =====
def load_data():
    """JSONファイルを読み込んでリストを返す。idがないレコードは補正して付与。"""
    if not os.path.exists(DATA_FILE):   # ファイルが無ければ空リスト
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = []   # ファイルが壊れていても安全に戻す

    # --- ここで id を補正 ---
    changed = False

    # 既存の最大IDを取得（idがないレコードがあってもOK）
    current_max = max((u.get("id", 0) for u in users), default=0)
    next_id = current_max + 1

    for u in users:
        if "id" not in u :
            u["id"] = next_id
            next_id += 1
            changed = True

    # 補正が入ったら保存して永続化（次回移行もOK）   
    if changed:
        save_data(users)
    return users
        
def save_data(data):
    """リストをJSONファイルに書き込む"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- HTML表示 ----------
@app.route("/")
def index():
    return render_template("index.html")

# ---------- データ受信 ----------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()   # JSから送られたJSONデータを受け取る
    name = data.get("name")
    email =data.get("email")

    if not name or not email:
        return jsonify({"status": "error", "message": "名前とメールは必須です。"}),400
    
    users = load_data()

    # 同じメールが既に存在していたらエラー
    if any(u["email"] == email for u in users):
        return jsonify({"status": "error", "message": "このメールはすでに登録済みです。"}),409
    
    # 登録する情報に自動的にIDを付与する（番号管理）
    new_id = max((u.get("id", 0) for u in users), default=0) + 1

    # 新しいユーザーを追加
    users.append({"id": new_id, "name": name, "email": email})
    save_data(users)
    return jsonify({"status": "success", "message": f"{name} さんを登録しました！"})

# ===== 一覧取得API（GET） =====
@app.route("/api/list", methods=["GET"])
def get_list():
    users = load_data()
    return jsonify(users)

# ===== 編集（Update） =====
@app.route("/api/update/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"status": "error", "message": "名前とメールは必須です。"}), 400

    users = load_data()

    # ★ 自分以外とのメール重複チェック（任意だが推奨）
    if any(u.get("email") == email and u.get("id") != user_id for u in users):
        return jsonify({"status": "error", "message": "このメールは別ユーザーで使用されています。"}), 409

    for user in users:
        if user.get("id") == user_id:   # get で安全比較
            user["name"] = name
            user["email"] = email
            save_data(users)
            return jsonify({"status": "success", "message": "更新しました。"})
    return jsonify({"status": "error", "message": "該当ユーザーが見つかりません。"}), 404

# ===== 削除（Delete） =====
@app.route("/api/delete/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    users = load_data()
    new_users = [u for u in users if u.get("id") != user_id]

    if len(new_users) == len(users):
        return jsonify({"status": "error", "message": "該当ユーザーが見つかりませんでした。"}), 404
    
    save_data(new_users)
    return jsonify({"status": "success", "message": "削除しました。"})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)