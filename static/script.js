const form = document.getElementById("registerForm");
const result = document.getElementById("result");

form.addEventListener("submit", async (e) => {
  e.preventDefault(); // ページリロード防止

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();

  // JS → Flask　へ送るデータ
  const payload = { name, email };

  try {
    // fetch() でPOST送信
    const res = await fetch("/api/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    // Flask からの応答を受け取る
    const data = await res.json();

    // 結果を表示
    result.textContent = data.message;
    result.style.color = "green";

  } catch (err) {
    console.error("通信エラー:", err);
    result.textContent = "通信に失敗しました。";
    result.style.color = "red";
  }
});