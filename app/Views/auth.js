// auth.js

const SECRET_KEY = "minha_chave_secreta_local"; // 🔒 troque por algo forte e único

// Criptografar string
function encrypt(text) {
  return CryptoJS.AES.encrypt(text, SECRET_KEY).toString();
}

// Descriptografar string
function decrypt(ciphertext) {
  try {
    const bytes = CryptoJS.AES.decrypt(ciphertext, SECRET_KEY);
    return bytes.toString(CryptoJS.enc.Utf8);
  } catch {
    return null;
  }
}

// Decodificar payload do JWT
function decodeJwt(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(c => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

// Função de validação do token
async function validarToken() {
  const token = localStorage.getItem("token");
  const username = localStorage.getItem("username");
  const encryptedPassword = localStorage.getItem("password");

  if (!token || !username || !encryptedPassword) {
    console.warn("⚠ Usuário não está logado!");
    window.location.href = "index.html";
    return;
  }

  const password = decrypt(encryptedPassword);
  if (!password) {
    console.warn("⚠ Erro ao descriptografar senha!");
    localStorage.clear();
    window.location.href = "index.html";
    return;
  }

  const payload = decodeJwt(token);
  if (!payload || !payload.exp) {
    console.warn("⚠ Token inválido!");
    localStorage.clear();
    window.location.href = "index.html";
    return;
  }

  const agora = Date.now() / 1000;
  if (payload.exp < agora) {
    console.warn("⚠ Token expirado, tentando renovar...");

    try {
      const params = new URLSearchParams();
      params.append("username", username);
      params.append("password", password);

      const response = await fetch("http://localhost:8000/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: params.toString(),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        localStorage.setItem("token", data.token);
        console.log("🔄 Novo token obtido com sucesso!");
      } else {
        console.error("❌ Não foi possível renovar token!");
        localStorage.clear();
        window.location.href = "index.html";
      }
      
    } catch (err) {
      console.error("❌ Erro ao renovar token:", err);
      localStorage.clear();
      window.location.href = "index.html";
    }
  } else {
    console.log("✅ Token válido, segue navegação.");
    return true;
  }
}

// document.addEventListener("DOMContentLoaded", () => {
//   const path = window.location.pathname;
//   const filename = path.substring(path.lastIndexOf("/") + 1);

//   if (filename !== "index.html") {
//     validarToken();
//   }
// });
// document.addEventListener("DOMContentLoaded", validarToken);
