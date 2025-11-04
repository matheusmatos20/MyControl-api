// Destacar página ativa automaticamente
// const links = document.querySelectorAll(".menu-lateral ul li a");
// links.forEach(link => {
//   if (link.href === window.location.href) {
//     link.parentElement.classList.add("active");
//   }
// });

// function alternarMenu() {
//   const menu = document.getElementById('menuLateral');
//   menu.classList.toggle('minimizado');
// }

const links = document.querySelectorAll(".menu-lateral ul li a");
links.forEach(link => {
  if (link.href === window.location.href) {
    link.parentElement.classList.add("active");
  }
});

function alternarMenu() {
  const menu = document.getElementById('menuLateral');
  const content = document.querySelector('.content'); // pega o wrapper

  menu.classList.toggle('minimizado');
  content.classList.toggle('recolhido'); // 🔹 ajusta o espaço
}

// Logout: limpa storage e volta para a Index
const logoutLink = document.getElementById('menuLogout');
if (logoutLink) {
  logoutLink.addEventListener('click', (e) => {
    e.preventDefault();
    try { localStorage.clear(); sessionStorage && sessionStorage.clear && sessionStorage.clear(); } catch {}
    // Redireciona para a página de login (Index)
    const target = '../Index/index.html';
    try { window.location.replace(target); } catch { window.location.href = target; }
  });
}
