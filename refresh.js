/* Datos siempre frescos + botón «Actualizar datos».
   - Cada carga usa una versión nueva para lexico/*.json; evita cachés obsoletas del CDN.
   - El botón añade una marca ?v=… que además salta la caché del CDN de GitHub Pages. */
(function(){
  // Una versión distinta en cada carga evita reutilizar JSON antiguos del CDN.
  var KEY='conlang-data-version', v=String(Date.now());
  try{sessionStorage.setItem(KEY,v)}catch(e){}
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
