
// JS comum: recolher/expandir menu lateral e pequenos utilitários
(function(){
  function $(sel, ctx){ return (ctx||document).querySelector(sel); }
  function $all(sel, ctx){ return Array.from((ctx||document).querySelectorAll(sel)); }

  // Toggle da sidebar via #menuToggle (se existir)
  var toggleBtn = $('#menuToggle');
  var sidebar = document.querySelector('.sidebar');
  if(toggleBtn && sidebar){
    toggleBtn.addEventListener('click', function(){
      // preferir classe no body para evitar "branco" no recolhimento
      document.body.classList.toggle('menu-collapsed');
      // fallback: alternar classe na própria sidebar
      sidebar.classList.toggle('collapsed');
    });
  }

  // Tornar tabelas automaticamente responsivas
  $all('table').forEach(function(tbl){
    if(!tbl.parentElement.classList.contains('table-responsive')){
      var wrap = document.createElement('div');
      wrap.className = 'table-responsive';
      tbl.parentNode.insertBefore(wrap, tbl);
      wrap.appendChild(tbl);
      tbl.classList.add('table');
    }
  });
})();
