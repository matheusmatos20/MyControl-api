// auth.js

const SECRET_KEY = "minha_chave_secreta_local"; // 🔒 troque por algo forte e único

const DEFAULT_AUTH_BASE = 'http://127.0.0.1:8000';
const resolvedAuthBase = (window.AUTH_BASE_URL || window.API_BASE_URL || DEFAULT_AUTH_BASE).replace(/\/$/, '');
const TOKEN_ENDPOINT = window.buildAuthUrl ? window.buildAuthUrl('/token') : `${resolvedAuthBase}/token`;

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

async function renovarToken(username, password) {

  try {

    const params = new URLSearchParams();

    params.append("username", username);

    params.append("password", password);



    const response = await fetch(TOKEN_ENDPOINT, {

      method: "POST",

      headers: { "Content-Type": "application/x-www-form-urlencoded" },

      body: params.toString(),

    });



    const data = await response.json();



    if (response.ok && data.success) {

      localStorage.setItem("token", data.token);

      if (data.empresa) {

        localStorage.setItem("empresa", data.empresa);

      }

      if (data.usuario) {

        localStorage.setItem("usuario", data.usuario);

      }

      console.log("🔄 Token renovado com sucesso.");

      return true;

    }



    console.error("❌ Não foi possível renovar token:", data.detail || response.status);

    return false;

  } catch (err) {

    console.error("❌ Erro ao renovar token:", err);

    return false;

  }

}



// Função de validação do token

async function validarToken() {

  const token = localStorage.getItem("token");

  const username = localStorage.getItem("username");

  const encryptedPassword = localStorage.getItem("password");



  if (!token || !username || !encryptedPassword) {

    console.warn("⚠ Usuário não está logado!");

    localStorage.clear();

    window.location.href = "index.html";

    return false;

  }



  const password = decrypt(encryptedPassword);

  if (!password) {

    console.warn("⚠ Erro ao descriptografar senha!");

    localStorage.clear();

    window.location.href = "index.html";

    return false;

  }



  const payload = decodeJwt(token);

  if (!payload || !payload.exp) {

    console.warn("⚠ Token inválido!");

    localStorage.clear();

    window.location.href = "index.html";

    return false;

  }



  const agora = Date.now() / 1000;

  const tempoRestante = payload.exp - agora;



  if (tempoRestante <= 0) {

    console.warn("⚠ Token expirado. Redirecionando para login.");

    localStorage.clear();

    window.location.href = "index.html";

    return false;

  }



  if (tempoRestante <= 300) {

    console.log("ℹ Token próximo do vencimento. Renovando...");

    const renovado = await renovarToken(username, password);

    if (!renovado) {

      localStorage.clear();

      window.location.href = "index.html";

      return false;

    }

    return true;

  }



  console.log("✅ Token válido, segue navegação.");

  return true;

}



// document.addEventListener("DOMContentLoaded", () => {
//   const path = window.location.pathname;
//   const filename = path.substring(path.lastIndexOf("/") + 1);

//   if (filename !== "index.html") {
//     validarToken();
//   }
// });
// document.addEventListener("DOMContentLoaded", validarToken);
