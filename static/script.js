const form = document.getElementById("registerForm");
const message = document.getElementById("message");
const tableBody = document.querySelector("#userTable tbody");
const submitBtn = document.getElementById("submitBtn");

// 追加：検索・ソートの参照
const searchInput = document.getElementById("search");
const sortSelect = document.getElementById("sort");

let editId = null; // 編集モードのときにIDを保持

// ===== APIから一覧を取得して表示 =====
async function fetchList() {
  
  // 検索語とソート条件をURLに付与
  const q = encodeURIComponent(searchInput?.value?.trim() || "");
  const sort = encodeURIComponent(sortSelect?.value || "id_desc");
  const res = await fetch(`/api/list?q=${q}&sort=${sort}`);
  const users = await res.json();

  // 表示をクリア
  tableBody.innerHTML = "";

  // 各行を作成
  users.forEach(user => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${user.id}</td>
      <td>${user.name}</td>
      <td>${user.email}</td>
      <td>
        <button class="edit" data-id="${user.id}">編集</button>
        <button class="delete" data-id="${user.id}">削除</button>
      </td>
    `;
    tableBody.appendChild(row);
  });
} 

// ===== フォーム送信処理 =====
form.addEventListener("submit", async (e) => {
  e.preventDefault(); // ページリロード防止

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();

  // JS → Flask　へ送るデータ
  const payload = { name, email };

  const url = editId ? `/api/update/${editId}` : "/api/register";
  const method = editId ? "PUT" : "POST";

  // fetch() でPOST送信
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  // Flask からの応答を受け取る
  const data = await res.json();

  message.textContent = data.message;
  message.style.color = res.ok ? "green" : "red";
  
  form.reset();
  editId = null;
  submitBtn.textContent = "登録";
  fetchList(); // 再取得して反映
});

// ===== 編集・削除ボタンのクリック =====
tableBody.addEventListener("click", async (e) => {
  const id = e.target.dataset.id;
  if (e.target.classList.contains("edit")) {
    // 編集モード
    const row = e.target.closest("tr");
    const name = row.children[1].textContent;
    const email = row.children[2].textContent;
    document.getElementById("name").value = name;
    document.getElementById("email").value = email;
    editId = Number(id);
    submitBtn.textContent = "更新";
  } else if (e.target.classList.contains("delete")) {
    if (!confirm("削除してよろしいですか？")) return;
    const res = await fetch(`/api/delete/${id}`, { method: "DELETE" });
    const data = await res.json();
    message.textContent = data.message;
    message.style.color = res.ok ? "green" : "red";
    fetchList();
  }
});

// 入力のたびに再取得（軽量用途ならOK）
searchInput.addEventListener("input", fetchList);
sortSelect.addEventListener("input", fetchList);

// 初回ロード時に一覧を読み込む
fetchList();