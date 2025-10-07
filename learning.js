// ==========================
// 🔹 要素の取得（HTMLとの接続）
// ==========================

// フォーム全体を取得
const form = document.getElementById("registerForm");

// メッセージ表示エリア（登録成功やエラーを表示する場所）
const message = document.getElementById("message");

// ユーザー一覧テーブルのtbody部分（データ行を追加する部分）
const tableBody = document.querySelector("#userTable tbody");

// 登録・更新ボタン
const submitBtn = document.getElementById("submitBtn");

// 編集モードのときに使う一時的なIDを保存する変数（null = 通常モード）
let editId = null;

// ======================================
// 🔹 一覧データを取得して表示する関数
// ======================================
async function fetchList() {
  // FlaskのAPI「/api/list」にアクセスして、データ一覧を取得
  const res = await fetch("/api/list");

  // 取得したレスポンス（JSON文字列）をJavaScriptオブジェクトに変換
  const users = await res.json();

  // 表示を一度クリアして、古いデータを消す
  tableBody.innerHTML = "";

  // 1人ずつデータを読み取り、表（tr要素）を作る
  users.forEach(user => {
    // <tr>（1行）を新しく作成
    const row = document.createElement("tr");

    // その中身（セル）をまとめて挿入（テンプレートリテラル）
    row.innerHTML = `
      <td>${user.id}</td>           <!-- ID列 -->
      <td>${user.name}</td>         <!-- 名前列 -->
      <td>${user.email}</td>        <!-- メール列 -->
      <td>
        <!-- 編集と削除のボタンを設置。data-id属性でIDを紐付け -->
        <button class="edit" data-id="${user.id}">編集</button>
        <button class="delete" data-id="${user.id}">削除</button>
      </td>
    `;

    // 完成した行をtbodyに追加（表に反映）
    tableBody.appendChild(row);
  });
}

// ==============================
// 🔹 フォーム送信イベント処理
// ==============================
form.addEventListener("submit", async (e) => {
  e.preventDefault();  // ← ページのリロードを防ぐ（デフォルト動作をキャンセル）

  // 入力欄から値を取得し、前後の空白を削除
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();

  // 送信するデータ（JSON形式）を準備
  const payload = { name, email };

  // 登録モードか編集モードかを判定
  // editId が null なら新規登録、値があれば更新モード
  const url = editId ? `/api/update/${editId}` : "/api/register";
  const method = editId ? "PUT" : "POST";

  // FlaskのAPIへリクエスト送信（fetchで通信）
  const res = await fetch(url, {
    method,                                   // POST または PUT
    headers: { "Content-Type": "application/json" }, // データ形式をJSONと明示
    body: JSON.stringify(payload)             // JSオブジェクトをJSON文字列に変換
  });

  // Flaskから返ってきたJSON（登録結果など）を受け取る
  const data = await res.json();

  // メッセージ欄に結果を表示（成功なら緑、エラーなら赤）
  message.textContent = data.message;
  message.style.color = res.ok ? "green" : "red";

  // フォームをリセット（入力内容を空に戻す）
  form.reset();

  // 編集モードを解除（次回送信時に登録モードに戻す）
  editId = null;
  submitBtn.textContent = "登録";

  // 一覧を再取得して最新データに更新
  fetchList();
});

// =========================================
// 🔹 テーブルのボタンクリックイベント処理
// =========================================

// イベント委譲：tbody全体にクリックイベントを登録
tableBody.addEventListener("click", async (e) => {
  // 押されたボタンの data-id（ユーザーのID）を取得
  const id = e.target.dataset.id;

  // 「編集」ボタンが押された場合
  if (e.target.classList.contains("edit")) {
    // ボタンのある行（tr要素）を取得
    const row = e.target.closest("tr");

    // 各セルの値を読み取って変数に格納
    const name = row.children[1].textContent;
    const email = row.children[2].textContent;

    // フォームに既存データをセット（編集モードに切り替え）
    document.getElementById("name").value = name;
    document.getElementById("email").value = email;

    // 編集対象のIDを記録
    editId = id;

    // ボタンのラベルを「更新」に変更
    submitBtn.textContent = "更新";

  // 「削除」ボタンが押された場合
  } else if (e.target.classList.contains("delete")) {
    // 確認ダイアログを表示（OKならtrueが返る）
    if (!confirm("削除してよろしいですか？")) return;

    // DELETEリクエストを送信
    const res = await fetch(`/api/delete/${id}`, { method: "DELETE" });

    // 結果をJSONとして取得
    const data = await res.json();

    // 結果メッセージを表示
    message.textContent = data.message;
    message.style.color = res.ok ? "green" : "red";

    // 最新の一覧を再描画
    fetchList();
  }
});

// =====================================
// 🔹 初期化処理（ページ読み込み時に実行）
// =====================================

// ページが開かれたら、自動的に一覧を読み込む
fetchList();