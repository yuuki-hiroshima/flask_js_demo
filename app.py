from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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

    print(f"受信データ: name={name}, email={email}")  # ターミナルで確認

    # 仮の処理（本来はDB保存など）
    response = {
        "status": "success",
        "message": f"{name} さん({email})を登録しました！"
    }
    return jsonify(response)  # JSON形式で返す

if __name__ == "__main__":
    app.run(debug=True)