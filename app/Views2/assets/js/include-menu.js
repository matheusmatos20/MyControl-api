(function(){
  // load menu.html into the container .sidebar (relative to page)
  function loadMenu(){
    var el = document.querySelector('.sidebar');
    if(!el) return;
    var path = 'menu.html';
    fetch(path).then(function(r){ return r.text(); }).then(function(html){
      el.innerHTML = html;
    }).catch(function(){ /* ignore failure */ });
  }
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded', loadMenu);
  } else loadMenu();
})();
