/* Datos frescos sin volver a descargar el léxico en cada página + botón «Actualizar datos».
   - En GitHub Pages (*.github.io) el CDN guarda copias hasta 10 min, así que cada carga pide
     lexico/*.json con una marca ?v=… nueva (descarga completa siempre).
   - En cualquier otro hosting (Cloudflare, local) el servidor marca los JSON como revalidables:
     el navegador pregunta si cambiaron y, si no, usa su copia (respuesta 304, casi instantánea).
   - El botón fuerza una descarga completa la siguiente vez que se cargue la página. */
(function(){
  var KEY='conlang-data-version', FORCE='conlang-data-force';
  var ghPages=/\.github\.io$/i.test(location.hostname);
  var force=false;
  try{force=sessionStorage.getItem(FORCE)==='1';sessionStorage.removeItem(FORCE)}catch(e){}
  var v=(ghPages||force)?String(Date.now()):'';
  try{if(v)sessionStorage.setItem(KEY,v)}catch(e){}
  var orig=window.fetch.bind(window);
  window.fetch=function(input,init){
    if(typeof input==='string' && /(^|\/)(lexico|textos)\/[^?#]+\.json(\?|#|$)/.test(input)){
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
      try{sessionStorage.setItem(KEY,String(Date.now()));sessionStorage.setItem(FORCE,'1')}catch(e){}
      var done=function(){location.reload()};
      if(window.caches&&caches.keys){caches.keys().then(function(ks){return Promise.all(ks.map(function(k){return caches.delete(k)}))}).then(done,done)}else done();
    });
    nav.appendChild(b);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',addButton);else addButton();
})();
