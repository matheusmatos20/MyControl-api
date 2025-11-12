// auth.js

const SECRET_KEY = "MC_4e1b96d3d6d14b0e8a2c9f7b5a3c1d0f-7E!q@Z#t$K%p^X&n*L(2)r+V=G?y";

const DEFAULT_AUTH_BASE = 'http://127.0.0.1:8000';
const resolvedAuthBase = (window.AUTH_BASE_URL || window.API_BASE_URL || DEFAULT_AUTH_BASE).replace(/\/$/, '');
const TOKEN_ENDPOINT = window.buildAuthUrl ? window.buildAuthUrl('/token') : `${resolvedAuthBase}/token`;
const LOGIN_PAGE = (() => {
  const configured = window.LOGIN_PAGE;
  if (configured) {
    try { return new URL(configured, window.location.href).href; } catch {}
  }
  const path = (window.location.pathname || '').replace(/\\/g, '/');
  const origin = window.location.origin || '';
  const lower = path.toLowerCase();
  // Prefer sempre Index como página de entrada
  let target = null;
  const idxApp = lower.lastIndexOf('/app/');
  if (idxApp !== -1) {
    target = origin + path.slice(0, idxApp + 5) + 'Views/Index/index.html';
  } else {
    const idxViews = lower.lastIndexOf('/views');
    if (idxViews !== -1) {
      target = origin + path.slice(0, idxViews + 7) + 'Index/index.html';
    }
  }
  if (target) return target;
  // Em ambientes como Azure SWA (raiz /), a página pública é /Index/index.html
  return origin + '/Index/index.html';
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
    // Evita manter a página protegida no histórico
    try { window.location.replace(LOGIN_PAGE); }
    catch { window.location.href = LOGIN_PAGE; }
    // Último recurso em caso de bloqueio pelo navegador
    setTimeout(() => { if (window.location.href !== LOGIN_PAGE) window.location.href = LOGIN_PAGE; }, 100);
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



// Validação automática em todas as telas, exceto a própria Index
function isIndexPage() {
  const path = (window.location.pathname || '').replace(/\\/g, '/').toLowerCase();
  // Considere público quando for servido de /views/index/ (dev) ou /index/ (SWA)
  return path.includes('/views/index/') || path.startsWith('/index/');
}

function scheduleValidate() {
  if (isIndexPage()) return; // não valida na index
  const run = () => { try { validarToken(); } catch (e) { console.warn('Falha ao validar token:', e); } };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run, { once: true });
  } else {
    // já carregado: valida imediatamente
    run();
  }
}

// Executa em todas as páginas que carregarem auth.js
try { scheduleValidate(); } catch {}


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
