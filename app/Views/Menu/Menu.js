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
