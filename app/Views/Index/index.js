document.addEventListener("DOMContentLoaded", () => {
  const btnLogin = document.getElementById("btn-login");
  const modalLogin = document.getElementById("login-modal");
  const closeLogin = document.getElementById("close-login");
  const formLogin = document.getElementById("form-login");
  const btnCtaFinal = document.getElementById('btn-cta-final');

  const DEFAULT_AUTH_BASE = 'http://127.0.0.1:8000';
  const resolvedAuthBase = (window.AUTH_BASE_URL || window.API_BASE_URL || DEFAULT_AUTH_BASE).replace(/\/$/, '');
  const tokenEndpoint = window.buildAuthUrl ? window.buildAuthUrl('/token') : `${resolvedAuthBase}/token`;

  // Abrir modal
  btnLogin.addEventListener("click", () => {
    modalLogin.style.display = "block";
  });

  // Fechar modal
  closeLogin.addEventListener("click", () => {
    modalLogin.style.display = "none";
  });

  // Fechar clicando fora do modal
  window.addEventListener("click", (e) => {
    if (e.target === modalLogin) {
      modalLogin.style.display = "none";
    }
  });

  // CTA final -> WhatsApp
  if (btnCtaFinal) {
    btnCtaFinal.addEventListener('click', (e) => {
      e.preventDefault();
      const number = '5513991547402';
      const text = encodeURIComponent('Olá! Tenho interesse no My Control.');
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
      const url = isMobile
        ? `https://wa.me/${number}?text=${text}`
        : `https://web.whatsapp.com/send?phone=${number}&text=${text}`;
      window.open(url, '_blank');
    });
  }

  // Login real
  formLogin.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email-login").value.trim();
    const senha = document.getElementById("senha-login").value.trim();

    if (!email || !senha) {
      alert("Preencha todos os campos!");
      return;
    }

    const btnSubmit = formLogin.querySelector("button");
    btnSubmit.disabled = true;
    btnSubmit.innerText = "Entrando...";

    try {
      // Preparar body x-www-form-urlencoded
      const params = new URLSearchParams();
      params.append("username", email);
      params.append("password", senha);


      
      // Requisição real para API de login
      const response = await fetch(tokenEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        // body: params.toString(),
        body: new URLSearchParams({
          username: email,
          password: senha
        })

      });

      // Recebe JSON do backend
      const data = await response.json();

      if (response.ok && data.success) {
        // Login bem-sucedido
        alert("✅ Login realizado com sucesso!");
        modalLogin.style.display = "none";
        formLogin.reset();

        // Salvar token para usar em outras páginas
        localStorage.setItem("token", data.token);
        localStorage.setItem("username", email);
        localStorage.setItem("password", encrypt(senha)); // ✅ criptografado
        if (data.empresa) {
          localStorage.setItem("empresa", data.empresa);
        }
        if (data.usuario) {
          localStorage.setItem("usuario", data.usuario);
        } else {
          localStorage.setItem("usuario", email);
        }

        
        // Redirecionar para Home
        window.location.href = "../Home/Home.html"; // ajuste o caminho se necessário
      } else {
        alert("❌ E-mail ou senha inválidos!");
      }
    } catch (err) {
      console.error("Erro:", err);
      alert("⚠ Erro na comunicação com o servidor.");
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.innerText = "Entrar";
    }
  });

  // -------------------------------
  // JSON auxiliar (mock) para debug
  // -------------------------------
  const loginMockData = [
    { email: "admin@teste.com", senha: "123456", success: true, token: "abc123token" },
    { email: "user@teste.com", senha: "123456", success: false, token: "" },
  ];

  // Função opcional para teste offline
  function fakeApiLogin(data) {
    return new Promise((resolve) => {
      console.log("📡 Tentando login (simulado)...", data);
      setTimeout(() => {
        const match = loginMockData.find(u => u.email === data.email && u.senha === data.senha);
        resolve(match || { success: false, token: "" });
      }, 800);
    });
  }

  // Cards de módulos agora são estáticos (sem navegação ou popups)
});

