// Alternar menu expandido/minimizado
function alternarMenu() {
  const menu = document.getElementById('menuLateral');
  if (menu) {
    menu.classList.toggle('minimizado');
  }
}

// Destacar página ativa automaticamente
document.addEventListener('DOMContentLoaded', () => {
  const links = document.querySelectorAll(".menu-lateral ul li a");
  links.forEach(link => {
    if (link.href === window.location.href) {
      link.parentElement.classList.add("active");
    }
  });

  // Condicional: esconder o menu se URL tiver "login"
  if (window.location.href.includes('login')) {
    const menuContainer = document.getElementById('menu-container');
    if (menuContainer) menuContainer.style.display = 'none';

    const toggleBtn = document.getElementById('botao-toggle-menu');
    if (toggleBtn) toggleBtn.style.display = 'none';
  }
});
