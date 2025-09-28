document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('login-modal');
  const closeBtn = document.getElementById('close-login');
  const formLogin = document.getElementById('form-login');
  const sectionDescobrir = document.getElementById('descobrir');
  const demoBtn = document.getElementById('btn-ver-demo');
  const faleBtn = document.getElementById('btn-fale-conosco');

  const DEFAULT_AUTH_BASE = 'http://127.0.0.1:8000';
  const resolvedAuthBase = (window.AUTH_BASE_URL || window.API_BASE_URL || DEFAULT_AUTH_BASE).replace(/\/$/, '');
  const tokenEndpoint = window.buildAuthUrl ? window.buildAuthUrl('/token') : `${resolvedAuthBase}/token`;

  const openModal = () => {
    if (modal) {
      modal.classList.add('show');
    }
  };

  const closeModal = () => {
    if (modal) {
      modal.classList.remove('show');
    }
  };

  ['btn-login', 'btn-cta', 'btn-cta-hero', 'btn-cta-final'].forEach((id) => {
    const trigger = document.getElementById(id);
    if (trigger) {
      trigger.addEventListener('click', openModal);
    }
  });

  if (demoBtn && sectionDescobrir) {
    demoBtn.addEventListener('click', () => {
      sectionDescobrir.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  if (faleBtn) {
    faleBtn.addEventListener('click', () => {
      window.location.href = 'mailto:contato@grantempo.com?subject=Quero%20saber%20mais%20sobre%20o%20Gran%20Tempo';
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', closeModal);
  }

  if (modal) {
    modal.addEventListener('click', (event) => {
      if (event.target === modal) {
        closeModal();
      }
    });
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeModal();
    }
  });

  if (formLogin) {
    formLogin.addEventListener('submit', async (event) => {
      event.preventDefault();

      const email = document.getElementById('email-login')?.value.trim();
      const senha = document.getElementById('senha-login')?.value.trim();

      if (!email || !senha) {
        alert('Preencha todos os campos!');
        return;
      }

      const submitBtn = formLogin.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Entrando...';
      }

      try {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', senha);

        const response = await fetch(tokenEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: params.toString()
        });

        const data = await response.json();

        if (response.ok && data.success) {
          alert('✅ Login realizado com sucesso!');
          closeModal();
          formLogin.reset();

          localStorage.setItem('token', data.token);
          localStorage.setItem('username', email);
          localStorage.setItem('password', encrypt(senha));
          if (data.empresa) {
            localStorage.setItem('empresa', data.empresa);
          }
          if (data.usuario) {
            localStorage.setItem('usuario', data.usuario);
          } else {
            localStorage.setItem('usuario', email);
          }

          window.location.href = '../Home/Home.html';
        } else {
          alert('❌ Usuário ou senha inválidos!');
        }
      } catch (error) {
        console.error('Erro ao tentar logar:', error);
        alert('⚠ Erro na comunicação com o servidor.');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Entrar';
        }
      }
    });
  }
});
