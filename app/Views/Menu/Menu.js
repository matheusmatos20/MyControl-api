(() => {
  const MOBILE_QUERY = window.matchMedia('(max-width: 1024px)');
  let menuElement = null;
  let contentElement = null;
  let overlayElement = null;
  let floatingToggle = null;

  const ready = () => {
    contentElement = contentElement || document.querySelector('.content');
    ensureOverlay();
    waitForMenu(initializeMenu);
    MOBILE_QUERY.addEventListener('change', handleBreakpointChange);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ready);
  } else {
    ready();
  }

  function ensureOverlay() {
    if (!document.body) {
      return;
    }
    if (!overlayElement) {
      overlayElement = document.createElement('div');
      overlayElement.className = 'menu-overlay';
      overlayElement.addEventListener('click', () => closeMobileMenu());
      document.body.appendChild(overlayElement);
    }
    if (!floatingToggle) {
      floatingToggle = document.createElement('button');
      floatingToggle.type = 'button';
      floatingToggle.className = 'menu-toggle-floating';
      floatingToggle.setAttribute('aria-label', 'Abrir menu lateral');
      floatingToggle.innerHTML = '☰';
      floatingToggle.addEventListener('click', () => alternarMenu());
      document.body.appendChild(floatingToggle);
    }
  }

  function waitForMenu(callback) {
    const existing = document.getElementById('menuLateral');
    if (existing) {
      callback(existing);
      return;
    }
    const observer = new MutationObserver(() => {
      const menu = document.getElementById('menuLateral');
      if (menu) {
        observer.disconnect();
        callback(menu);
      }
    });
    observer.observe(document.body || document.documentElement, {
      childList: true,
      subtree: true,
    });
  }

  function initializeMenu(menu) {
    menuElement = menu;
    highlightActiveLink(menu);
    bindLogout(menu);

    menu.addEventListener('click', (event) => {
      if (!MOBILE_QUERY.matches) {
        return;
      }
      const link = event.target.closest('a');
      if (link) {
        closeMobileMenu();
      }
    });

    if (MOBILE_QUERY.matches) {
      menu.classList.remove('minimizado');
      if (contentElement) {
        contentElement.classList.remove('recolhido');
      }
    }
  }

  function highlightActiveLink(menu) {
    const currentUrl = window.location.href.split('#')[0];
    menu.querySelectorAll('ul li a').forEach((link) => {
      const cleanLink = link.href.split('#')[0];
      if (currentUrl === cleanLink) {
        link.parentElement.classList.add('active');
      } else {
        link.parentElement.classList.remove('active');
      }
    });
  }

  function bindLogout(menu) {
    const logoutLink = menu.querySelector('#menuLogout');
    if (!logoutLink) {
      return;
    }
    logoutLink.addEventListener('click', (event) => {
      event.preventDefault();
      try {
        localStorage.clear();
        if (typeof sessionStorage !== 'undefined') {
          sessionStorage.clear();
        }
      } catch (error) {
        console.warn('Nao foi possivel limpar o storage durante logout.', error);
      }
      const target = '../Index/index.html';
      try {
        window.location.replace(target);
      } catch {
        window.location.href = target;
      }
    });
  }

  function handleBreakpointChange(event) {
    const menu = menuElement || document.getElementById('menuLateral');
    if (!menu) {
      return;
    }
    if (event.matches) {
      // Entrou em modo mobile
      menu.classList.remove('minimizado');
      if (contentElement) {
        contentElement.classList.remove('recolhido');
      }
    } else {
      // Voltou para desktop
      closeMobileMenu();
    }
  }

  function closeMobileMenu() {
    const menu = menuElement || document.getElementById('menuLateral');
    if (!menu) {
      return;
    }
    menu.classList.remove('mobile-aberto');
    document.body && document.body.classList.remove('menu-locked');
    if (overlayElement) {
      overlayElement.classList.remove('visivel');
    }
    if (floatingToggle) {
      floatingToggle.classList.remove('active');
    }
  }

  function alternarMenu(forceState) {
    const menu = menuElement || document.getElementById('menuLateral');
    if (!menu) {
      return;
    }
    const isMobile = MOBILE_QUERY.matches;
    if (isMobile) {
      const shouldOpen = typeof forceState === 'boolean'
        ? forceState
        : !menu.classList.contains('mobile-aberto');
      menu.classList.toggle('mobile-aberto', shouldOpen);
      document.body && document.body.classList.toggle('menu-locked', shouldOpen);
      if (overlayElement) {
        overlayElement.classList.toggle('visivel', shouldOpen);
      }
      if (floatingToggle) {
        floatingToggle.classList.toggle('active', shouldOpen);
      }
      if (!shouldOpen && contentElement) {
        contentElement.classList.remove('recolhido');
      }
      return;
    }

    menu.classList.toggle('minimizado');
    if (contentElement) {
      contentElement.classList.toggle('recolhido', menu.classList.contains('minimizado'));
    }
  }

  // Disponibiliza a função globalmente para o botão inline do menu
  window.alternarMenu = alternarMenu;
})();
