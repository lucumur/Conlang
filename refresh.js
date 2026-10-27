/* Datos siempre frescos + botón «Actualizar datos».
   - Toda petición a lexico/*.json se revalida con el servidor (no usa copia vieja del navegador).
   - El botón añade una marca ?v=… que además salta la caché del CDN de GitHub Pages. */
(function(){
  var KEY='conlang-data-version', v=null;
  try{v=sessionStorage.getItem(KEY)}catch(e){}
  var orig=window.fetch.bind(window);
  window.fetch=function(input,init){
    if(typeof input==='string' && /(^|\/)lexico\/[^?#]+\.json(\?|#|$)/.test(input)){
      if(v) input+=(input.indexOf('?')<0?'?':'&')+'v='+v;
      init=Object.assign({cache:v?'reload':'no-cache'},init||{});
    }
    return orig(input,init);
  };
  function addButton(){
    var nav=document.querySelector('.site-nav');
    if(!nav||nav.querySelector('.refresh-data'))return;
    var b=document.createElement('button');
    b.type='button';b.className='refresh-data';
    b.title='Descarga de nuevo el léxico ignorando la caché';
    b.textContent='↻ Actualizar datos';
    b.addEventListener('click',function(){
      b.disabled=true;b.textContent='Actualizando…';
      try{sessionStorage.setItem(KEY,String(Date.now()))}catch(e){}
      var done=function(){location.reload()};
      if(window.caches&&caches.keys){caches.keys().then(function(ks){return Promise.all(ks.map(function(k){return caches.delete(k)}))}).then(done,done)}else done();
    });
    nav.appendChild(b);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',addButton);else addButton();
})();
