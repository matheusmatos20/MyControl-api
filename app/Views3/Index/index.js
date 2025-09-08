document.addEventListener("DOMContentLoaded", () => {
  const btnLogin = document.getElementById("btn-login");
  const modalLogin = document.getElementById("login-modal");
  const closeLogin = document.getElementById("close-login");
  const formLogin = document.getElementById("form-login");

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

  // Simulação de login
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
      // Simulação de API de login
      const response = await fakeApiLogin({ email, senha });

      if (response.success) {
        // Login bem-sucedido
        alert("✅ Login realizado com sucesso!");
        modalLogin.style.display = "none";
        formLogin.reset();

        // Redirecionar para outra página
        window.location.href = "Home.html"; // coloque o caminho da página desejada
      } else {
        alert("❌ E-mail ou senha inválidos!");
      }
    } catch (err) {
      console.error(err);
      alert("⚠ Erro na comunicação com o servidor.");
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.innerText = "Entrar";
    }
  });

  // Função simulando API de login
  function fakeApiLogin(data) {
    return new Promise((resolve) => {
      console.log("📡 Tentando login (simulado)...", data);
      setTimeout(() => {
        // Sucesso se email contém "admin"
        resolve({ success: data.email.includes("admin") });
      }, 1200);
    });
  }
});
