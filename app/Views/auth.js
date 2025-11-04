// auth.js

const SECRET_KEY = "minha_chave_secreta_local"; // 🔒 troque por algo forte e único

const DEFAULT_AUTH_BASE = 'http://127.0.0.1:8000';
const resolvedAuthBase = (window.AUTH_BASE_URL || window.API_BASE_URL || DEFAULT_AUTH_BASE).replace(/\/$/, '');
const TOKEN_ENDPOINT = window.buildAuthUrl ? window.buildAuthUrl('/token') : `${resolvedAuthBase}/token`;
const LOGIN_PAGE = (() => {
  const configured = window.LOGIN_PAGE;
  if (configured) {
    try {
      return new URL(configured, window.location.href).href;
    } catch (error) {
      console.warn("⚠ Não foi possível resolver LOGIN_PAGE configurado, usando padrão.", error);


    }
  }
  try {
    return new URL('../Index/index.html', window.location.href).href;
  } catch (error) {
    return '../Index/index.html';
  }
})();

let redirectingToLogin = false;

function logoutAndRedirect(reason) {
  if (reason) {
    console.warn(reason);
  }
  if (redirectingToLogin) {
    return;
  }
  redirectingToLogin = true;
  try {
    localStorage.clear();
  } catch (error) {
    console.error('Erro ao limpar storage durante logout:', error);
  }
  if (window.location.href !== LOGIN_PAGE) {
    window.location.href = LOGIN_PAGE;
  }
}


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
    logoutAndRedirect();
    return false;

  }



  const password = decrypt(encryptedPassword);

  if (!password) {

    console.warn("⚠ Erro ao descriptografar senha!");
    logoutAndRedirect();
    return false;

  }



  const payload = decodeJwt(token);

  if (!payload || !payload.exp) {

    console.warn("⚠ Token inválido!");
    logoutAndRedirect();
    return false;

  }



  const agora = Date.now() / 1000;

  const tempoRestante = payload.exp - agora;



  if (tempoRestante <= 0) {

    console.warn("⚠ Token expirado. Redirecionando para login.");
    logoutAndRedirect();
    return false;

  }



  if (tempoRestante <= 300) {

    console.log("ℹ Token próximo do vencimento. Renovando...");

    const renovado = await renovarToken(username, password);

    if (!renovado) {
        logoutAndRedirect();

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


function hasBearerAuthorization(input, init) {
  const sources = [];
  if (init && init.headers) {
    sources.push(init.headers);
  }
  if (typeof Request !== 'undefined' && input instanceof Request) {
    sources.push(input.headers);
  }
  for (const source of sources) {
    try {
      const headers = source instanceof Headers ? source : new Headers(source);
      const auth = headers.get('Authorization') || headers.get('authorization');
      if (auth && auth.toLowerCase().startsWith('bearer')) {
        return true;
      }
    } catch (error) {
      console.error('Erro ao analisar cabecalhos de autorizacao:', error);
    }
  }
  return false;
}

(function attachAuthInterceptor() {
  if (typeof window === 'undefined' || !window.fetch) {
    return;
  }
  const originalFetch = window.fetch.bind(window);
  window.fetch = async function (input, init = {}) {
    const response = await originalFetch(input, init);
    try {
      if (response && response.status === 401 && hasBearerAuthorization(input, init)) {
        logoutAndRedirect('Sessao expirada. Faca login novamente.');
      }
    } catch (error) {
      console.error('Erro no interceptor de autenticacao:', error);
    }
    return response;
  };
})();
