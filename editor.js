/* Modo edición del léxico.
   - Escribe directamente en el repositorio lucumur/Conlang mediante la API de GitHub,
     con un token personal (fine-grained) guardado solo en este navegador.
   - Cada guardado es UN commit que incluye el archivo de letra (o morphemes.json)
     y lexico/index.json ya regenerado; el workflow del repo después actualiza history.json.
   - Con el modo edición activo, la página lee lexico/*.json desde la API (siempre fresco),
     no desde la copia publicada de GitHub Pages. */
(function () {
  'use strict';
  var OWNER = 'lucumur', REPO = 'Conlang', BRANCH = 'main', API = 'https://api.github.com';
  var LETTER_FILES = [['A','a'],['B','b'],['C','c'],['Ĉ','circ-c'],['D','d'],['E','e'],['F','f'],['G','g'],['Ĝ','circ-g'],
    ['I','i'],['J','j'],['Ĵ','circ-j'],['K','k'],['L','l'],['M','m'],['N','n'],['O','o'],['P','p'],['R','r'],['S','s'],
    ['Ŝ','circ-s'],['T','t'],['Θ','theta'],['U','u'],['V','v'],['Z','z'],['Ẑ','circ-z']];

  /* ---------- Índice: réplica exacta de scripts/build_lexicon_index.py ---------- */
  function has(o, k) { return o != null && Object.prototype.hasOwnProperty.call(o, k); }
  function get(o, k, d) { return has(o, k) ? o[k] : d; }
  function labels(tags) { return (tags || []).map(function (t) { return get(t, 'label', ''); }); }
  function letterPart(letter, key, data) {
    var roots = [], words = [];
    get(data, 'entries', []).forEach(function (e) {
      if (get(e, 'kind', null) === 'other') return;
      var parts = [get(e, 'form', ''), get(e, 'gloss', ''), get(e, 'etymology', null) || ''].concat(labels(get(e, 'tags', null)));
      get(e, 'words', []).forEach(function (w) {
        var sf = get(w, 'semantic_fields', []) || [], notes = get(w, 'notes', []) || [];
        words.push({
          id: w.id, root_id: e.id, root_form: get(e, 'form', ''), root_gloss: get(e, 'gloss', ''),
          letter: letter, key: key,
          form: get(w, 'form', ''), gloss: get(w, 'gloss', ''),
          ...(get(w, 'emoji', '') ? { emoji: get(w, 'emoji', '') } : {}),
          analysis_text: get(w, 'analysis_text', ''), analysis_html: get(w, 'analysis_html', ''),
          tags: labels(get(w, 'tags', null)),
          refs: get(w, 'refs', []).map(function (r) { return get(r, 'id', null); }).filter(Boolean),
          semantic_fields: sf, notes: notes,
          search: [get(w, 'form', ''), get(w, 'gloss', ''), get(e, 'form', ''), get(e, 'gloss', ''), get(w, 'analysis_text', '')]
            .concat(labels(get(w, 'tags', null)), sf, notes).join(' ')
        });
      });
      roots.push({ id: e.id, letter: letter, key: key, form: get(e, 'form', ''), gloss: get(e, 'gloss', ''),
        tags: labels(get(e, 'tags', null)), etymology: get(e, 'etymology', null), search: parts.join(' ') });
    });
    return { roots: roots, words: words };
  }
  function morphPart(mdata) {
    return get(mdata, 'morphemes', []).map(function (m) {
      return { id: m.id, letter: get(m, 'letter', ''), form: get(m, 'form', ''), gloss: get(m, 'gloss', ''),
        tags: labels(get(m, 'tags', null)), search: [get(m, 'form', ''), get(m, 'gloss', '')].concat(labels(get(m, 'tags', null))).join(' ') };
    });
  }
  /* letterData: {key: datos completos} para las letras cambiadas; el resto se toma del índice anterior */
  function buildIndex(prev, letterData, mdata) {
    var roots = [], words = [];
    LETTER_FILES.forEach(function (lf) {
      var letter = lf[0], key = lf[1];
      if (letterData && has(letterData, key)) {
        var p = letterPart(letter, key, letterData[key]);
        roots.push.apply(roots, p.roots); words.push.apply(words, p.words);
      } else {
        roots.push.apply(roots, prev.roots.filter(function (r) { return r.key === key; }));
        words.push.apply(words, prev.words.filter(function (w) { return w.key === key; }));
      }
    });
    var morphemes = mdata ? morphPart(mdata) : prev.morphemes;
    return {
      schema_version: 1,
      letters: LETTER_FILES.map(function (lf) { return { section: 'sec-' + lf[1], letter: lf[0], key: lf[1], file: 'lexico/' + lf[1] + '.json' }; }),
      roots: roots, words: words, morphemes: morphemes,
      counts: { roots: roots.length, words: words.length, morphemes: morphemes.length }
    };
  }
  if (typeof module !== 'undefined' && module.exports) { module.exports = { buildIndex: buildIndex, LETTER_FILES: LETTER_FILES }; return; }

  /* ---------- Estado ---------- */
  var TK = 'conlang-gh-token', EK = 'conlang-edit-mode', RK = 'conlang-edit-ref';
  function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } }
  function token() { return ls(TK); }
  function editOn() { return !!token() && ls(EK) === '1'; }
  function currentRef() {
    try { var o = JSON.parse(sessionStorage.getItem(RK) || 'null'); if (o && Date.now() - o.t < 10 * 60 * 1000) return o.sha; } catch (e) {}
    return BRANCH;
  }
  function setRef(sha) { try { sessionStorage.setItem(RK, JSON.stringify({ sha: sha, t: Date.now() })); } catch (e) {} }

  var baseFetch = window.fetch.bind(window);
  function contentsURL(path, ref) { return API + '/repos/' + OWNER + '/' + REPO + '/contents/' + path + '?ref=' + encodeURIComponent(ref || BRANCH); }
  function headers(raw, json) {
    var h = { Authorization: 'Bearer ' + token(), Accept: raw ? 'application/vnd.github.raw+json' : 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' };
    if (json) h['Content-Type'] = 'application/json';
    return h;
  }

  /* En modo edición, lexico/*.json se lee desde la API (fresco); si falla, cae a la copia publicada. */
  if (editOn()) {
    window.fetch = function (input, init) {
      if (typeof input === 'string') {
        var m = input.match(/^(?:\.\/)?lexico\/([^?#\/]+\.json)/);
        if (m) {
          return baseFetch(contentsURL('lexico/' + m[1], currentRef()), { headers: headers(true), cache: 'no-store' })
            .then(function (r) { return r.ok ? r : baseFetch(input, init); }, function () { return baseFetch(input, init); });
        }
      }
      return baseFetch(input, init);
    };
  }

  /* ---------- API de GitHub ---------- */
  function gh(path, opt) {
    opt = opt || {};
    return baseFetch(API + path, { method: opt.method || 'GET', headers: headers(opt.raw, !!opt.body), body: opt.body ? JSON.stringify(opt.body) : undefined, cache: 'no-store' })
      .then(function (r) {
        if (!r.ok) return r.text().then(function (t) {
          var msg = t; try { msg = JSON.parse(t).message || t; } catch (e) {}
          var err = new Error('GitHub ' + r.status + ': ' + msg); err.status = r.status; throw err;
        });
        return opt.raw ? r.text() : (r.status === 204 ? null : r.json());
      });
  }
  var RP = '/repos/' + OWNER + '/' + REPO;
  function readJSON(path, ref) { return gh('/repos/' + OWNER + '/' + REPO + '/contents/' + path + '?ref=' + encodeURIComponent(ref || BRANCH), { raw: true }).then(JSON.parse); }

  /* Un guardado = una transacción: leer en la cabeza de main, aplicar el cambio, regenerar el índice,
     y crear un único commit. Si main avanzó entretanto, se repite sobre la versión nueva. */
  function transact(apply) {
    var attempt = 0;
    function run() {
      attempt++;
      var cache = {}, base, baseTree;
      function read(p) { if (!cache[p]) cache[p] = readJSON(p, base); return cache[p]; }
      return gh(RP + '/git/ref/heads/' + BRANCH).then(function (ref) {
        base = ref.object.sha;
        return gh(RP + '/git/commits/' + base);
      }).then(function (c) {
        baseTree = c.tree.sha;
        return Promise.resolve(apply({ read: read }));
      }).then(function (res) {
        var letterData = {}, mdata = null;
        Object.keys(res.files).forEach(function (p) {
          var m = p.match(/^lexico\/(.+)\.json$/);
          if (m && m[1] === 'morphemes') mdata = res.files[p]; else if (m) letterData[m[1]] = res.files[p];
        });
        return read('lexico/index.json').then(function (idx) {
          var out = Object.keys(res.files).map(function (p) { return [p, JSON.stringify(res.files[p], null, 2) + '\n']; });
          out.push(['lexico/index.json', JSON.stringify(buildIndex(idx, letterData, mdata))]);
          return Promise.all(out.map(function (f) {
            return gh(RP + '/git/blobs', { method: 'POST', body: { content: f[1], encoding: 'utf-8' } })
              .then(function (b) { return { path: f[0], mode: '100644', type: 'blob', sha: b.sha }; });
          }));
        }).then(function (tree) {
          return gh(RP + '/git/trees', { method: 'POST', body: { base_tree: baseTree, tree: tree } });
        }).then(function (t) {
          return gh(RP + '/git/commits', { method: 'POST', body: { message: res.message + '\n\nEditado desde la página web (modo edición).', tree: t.sha, parents: [base] } });
        }).then(function (c) {
          return gh(RP + '/git/refs/heads/' + BRANCH, { method: 'PATCH', body: { sha: c.sha, force: false } }).then(function () {
            setRef(c.sha); res.sha = c.sha; return res;
          });
        });
      }).catch(function (err) {
        if ((err.status === 422 || err.status === 409) && attempt < 4 && !err.fatal) return run();
        throw err;
      });
    }
    return run();
  }
  function fail(msg) { var e = new Error(msg); e.fatal = true; throw e; }

  /* ---------- Utilidades del léxico ---------- */
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var SLUG = { 'ĉ': 'cx', 'ĝ': 'gx', 'ĥ': 'hx', 'ĵ': 'jx', 'ŝ': 'sx', 'ẑ': 'zx', 'ŭ': 'ux', 'θ': 'th' };
  function slug(s) {
    return String(s || '').toLocaleLowerCase('es').replace(/[ĉĝĥĵŝẑŭθ]/g, function (c) { return SLUG[c]; })
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'x';
  }
  function uniqueId(base, taken) { var id = base, n = 2; while (taken.has(id)) id = base + '-' + (n++); return id; }
  function bare(form) { return String(form || '').replace(/^\*/, '').replace(/\s*\(.*\)\s*$/, '').trim(); }
  function rootLabel(form) { return bare(form).replace(/^-+|-+$/g, ''); }
  function letterOf(form) {
    var ch = Array.from(bare(form).replace(/^-+/, '').toLocaleUpperCase('es'))[0] || '';
    var lf = LETTER_FILES.find(function (x) { return x[0] === ch; });
    return lf ? { letter: lf[0], key: lf[1] } : null;
  }
  var coll = new Intl.Collator('es', { sensitivity: 'base' });
  function insertSorted(list, item, cmpKey) {
    var i = list.findIndex(function (x) { return coll.compare(cmpKey(x), cmpKey(item)) > 0; });
    if (i < 0) list.push(item); else list.splice(i, 0, item);
  }
  function lines(s) { return String(s || '').split('\n').map(function (x) { return x.trim(); }).filter(Boolean); }
  function sameJSON(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

  var ROOT_RELATION = ['Nat-Plen','Nat-Mod','Nat-Red','Nova'];
  var EXTERNAL_ETYM = ['Latin','Griego','Germanico','Frances','Anglo','Italico','Iberico','Eslavo','Arabe','Celta','Indopersa','Turquico','Sinico'];
  var ORIGIN = ROOT_RELATION.concat(EXTERNAL_ETYM,['Esper','Neo']);
  var ORIGIN_CLASS = {}, ORIGIN_LABEL = {};
  ORIGIN.forEach(function (l) { ORIGIN_CLASS[l.toLowerCase()] = l.toLowerCase(); ORIGIN_LABEL[l.toLowerCase()] = l; });
  var ETYM_ALIASES = {"latín":"Latin","germánico":"Germanico","francés":"Frances","itálico":"Italico","ibérico":"Iberico","árabe":"Arabe","túrquico":"Turquico","sínico":"Sinico","helénico":"Griego","helenico":"Griego","slavo":"Eslavo","romance":"Italico","espanol":"Iberico","español":"Iberico","portugues":"Iberico","portugués":"Iberico","indico":"Indopersa","persa":"Indopersa"};
  Object.keys(ETYM_ALIASES).forEach(function (l) { var canonical = ETYM_ALIASES[l]; ORIGIN_CLASS[l] = canonical.toLowerCase(); ORIGIN_LABEL[l] = canonical; });
  /* Etiquetas: se conservan tal cual las que ya existían; las nuevas toman clase de origen si la reconocen. */
  function tagsFrom(labelsList, previous) {
    var prevBy = {};
    (previous || []).forEach(function (t) { prevBy[String(t.label).toLowerCase()] = t; });
    return labelsList.map(function (l) {
      var k = l.toLowerCase();
      if (ORIGIN_CLASS[k]) return { class: ORIGIN_CLASS[k], label: ORIGIN_LABEL[k] };
      return prevBy[k] || { class: 'generic', label: l };
    });
  }

  /* ---------- Análisis morfológico ---------- */
  var PEND = ' <span class="meta-extra">(pendiente)</span>';
  function unesc(s) { var d = document.createElement('textarea'); d.innerHTML = s; return d.value; }
  function parseAnalysis(html) {
    if (!html) return { segs: [], pend: false };
    var h = html, pend = false;
    if (h.slice(-PEND.length) === PEND) { pend = true; h = h.slice(0, -PEND.length); }
    var segs = [], parts = h.split(' + ');
    for (var i = 0; i < parts.length; i++) {
      var m = parts[i].match(/^<a class="morph-link" href="#([^"]+)">([^<]*)<\/a>(\?)?$/);
      if (m) { segs.push({ ref: m[1], text: unesc(m[2]), q: !!m[3] }); continue; }
      m = parts[i].match(/^([^<>]*?)(\?)?$/);
      if (m && m[1]) { segs.push({ ref: null, text: unesc(m[1]), q: !!m[2] }); continue; }
      return null;
    }
    return { segs: segs, pend: pend };
  }
  function segsHTML(segs, pend) {
    var body = segs.filter(function (s) { return s.text.trim(); }).map(function (s) {
      return (s.ref ? '<a class="morph-link" href="#' + esc(s.ref) + '">' + esc(s.text.trim()) + '</a>' : esc(s.text.trim())) + (s.q ? '?' : '');
    }).join(' + ');
    return body ? body + (pend ? PEND : '') : '';
  }
  function analysisFromHTML(html) {
    var d = document.createElement('div'); d.innerHTML = html || '';
    var seen = {}, refs = [];
    d.querySelectorAll('a.morph-link[href^="#"]').forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      if (id && !seen[id]) { seen[id] = 1; refs.push({ id: id, label: a.textContent }); }
    });
    return { analysis_html: html || '', analysis_text: d.textContent.replace(/\s+/g, ' ').trim(), refs: refs };
  }

  /* ---------- Índice para autocompletar ---------- */
  var idxPromise = null;
  function loadIndex() {
    if (!idxPromise) idxPromise = readJSON('lexico/index.json', currentRef()).catch(function () { return readJSON('lexico/index.json', BRANCH); });
    return idxPromise;
  }

  /* ---------- Interfaz ---------- */
  var CSS = [
    '.ce-btn{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border:1px solid var(--line);border-radius:999px;background:var(--paper);color:var(--ink);font:inherit;font-size:.86rem;font-weight:600;cursor:pointer;text-decoration:none}',
    '.ce-btn:hover{border-color:var(--accent);color:var(--accent)}.ce-btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}.ce-btn.primary:hover{filter:brightness(1.1);color:#fff}',
    '.ce-btn.danger{color:#b42318;border-color:#f1c4bf}.ce-btn.danger:hover{background:#fdecea}.ce-btn:disabled{opacity:.55;cursor:wait}',
    '.ce-btn.small{padding:1px 8px;font-size:.74rem;font-weight:700}',
    '.ce-toggle{margin-left:4px;padding:3px 10px;border:1px solid var(--line);border-radius:999px;background:var(--paper);color:var(--muted);font:inherit;font-size:.86rem;cursor:pointer}',
    '.ce-toggle:hover{border-color:var(--accent);color:var(--accent)}.ce-toggle.on{background:#eef2ff;border-color:var(--accent);color:var(--accent);font-weight:700}',
    '.ce-bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 20px;padding:10px 12px;border:1px dashed var(--accent);border-radius:12px;background:#f5f6ff}',
    '.ce-bar .ce-bar-label{font-size:.74rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-right:4px}',
    '.ce-inline{margin-left:6px;vertical-align:middle}',
    'dialog.ce-dialog{width:min(760px,calc(100% - 24px));max-height:calc(100vh - 32px);padding:0;border:1px solid var(--line);border-radius:18px;background:var(--paper);color:var(--ink);box-shadow:0 24px 80px rgba(30,27,22,.25)}',
    'dialog.ce-dialog::backdrop{background:rgba(37,35,31,.35)}',
    '.ce-dialog form{display:flex;flex-direction:column;max-height:calc(100vh - 34px)}',
    '.ce-head{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:16px 22px;border-bottom:1px solid var(--line)}.ce-head h2{margin:0;font-size:1.25rem}',
    '.ce-x{border:0;background:none;font-size:1.4rem;line-height:1;color:var(--muted);cursor:pointer}',
    '.ce-body{padding:18px 22px;overflow:auto;display:grid;gap:14px}',
    '.ce-foot{display:flex;gap:8px;align-items:center;padding:14px 22px;border-top:1px solid var(--line)}.ce-foot .ce-spacer{flex:1}',
    '.ce-field{display:grid;gap:5px}.ce-field>span{font-size:.72rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}',
    '.ce-field small{color:var(--muted);font-size:.78rem}',
    '.ce-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}',
    '.ce-dialog input[type=text],.ce-dialog input[type=password],.ce-dialog input:not([type]),.ce-dialog textarea{width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:9px;background:#fff;color:var(--ink);font:inherit;font-size:.95rem}',
    '.ce-dialog textarea{min-height:64px;resize:vertical}.ce-dialog input:focus,.ce-dialog textarea:focus{outline:2px solid #c7cbff;border-color:var(--accent)}',
    '.ce-word-form-row{display:flex;align-items:center;gap:8px}.ce-word-form-row>input{min-width:0;flex:1}',
    '.ce-emoji-picker{position:relative;flex:0 0 auto}.ce-emoji-trigger{display:grid;place-items:center;width:43px;height:43px;padding:0;border:1px solid var(--line);border-radius:10px;background:#fff;font-size:1.5rem;line-height:1;cursor:pointer}.ce-emoji-trigger:hover,.ce-emoji-trigger:focus-visible{border-color:var(--accent);outline:none}',
    '.ce-emoji-panel{position:absolute;top:calc(100% + 7px);left:0;z-index:50;width:min(350px,calc(100vw - 56px));max-height:min(480px,65vh);overflow-y:auto;padding:12px;border:1px solid var(--line);border-radius:13px;background:var(--paper);box-shadow:0 15px 40px rgba(30,27,22,.2);display:grid;gap:10px}.ce-emoji-panel[hidden]{display:none}',
    '.ce-emoji-results{display:grid;gap:11px;max-height:255px;overflow-y:auto}.ce-emoji-group{display:grid;gap:6px}.ce-emoji-group-title{font-size:.74rem;color:var(--muted);font-weight:800}.ce-emoji-grid{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:2px}',
    '.ce-emoji-option{display:grid;place-items:center;min-width:0;height:34px;padding:0;border:1px solid transparent;border-radius:7px;background:transparent;font-size:1.34rem;cursor:pointer}.ce-emoji-option:hover,.ce-emoji-option:focus-visible{border-color:var(--accent);background:#eef2ff;outline:none}',
    '.ce-emoji-paste{display:flex;gap:6px}.ce-emoji-paste input{min-width:0;flex:1}.ce-emoji-paste button{white-space:nowrap}.ce-emoji-empty{font-size:.83rem;color:var(--muted)}',
    '.ce-mono{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace!important}',
    '.ce-chips{display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:6px;border:1px solid var(--line);border-radius:9px;background:#fff}',
    '.ce-chips input{flex:1 1 140px;border:0!important;padding:3px 4px!important;outline:0!important}',
    '.ce-chip{display:inline-flex;align-items:center;gap:4px;padding:2px 4px 2px 9px;border-radius:999px;background:#ece9e2;font-size:.82rem;font-weight:600}',
    '.ce-chip button{border:0;background:none;cursor:pointer;color:var(--muted);font-size:.95rem;line-height:1;padding:0 3px}',
    '.ce-segs{display:grid;gap:6px}.ce-seg{display:grid;grid-template-columns:minmax(0,1fr) auto auto auto auto;gap:6px;align-items:center}',
    '.ce-seg .ce-link{font-size:.72rem;color:var(--muted);white-space:nowrap;max-width:190px;overflow:hidden;text-overflow:ellipsis}.ce-seg .ce-link.linked{color:var(--accent);font-weight:700}',
    '.ce-pick{max-width:190px;font:inherit;font-size:.74rem;padding:3px 4px;border:1px solid var(--accent);border-radius:7px;background:#fff;color:var(--accent)}',
    '.ce-seg input.ce-linked{border-color:var(--accent)!important;background:#f5f6ff!important}',
    '.ce-seg label{font-size:.78rem;color:var(--muted);white-space:nowrap}',
    '.ce-ico{border:1px solid var(--line);background:#fff;border-radius:7px;width:28px;height:28px;cursor:pointer;color:var(--muted)}.ce-ico:hover{color:var(--accent);border-color:var(--accent)}',
    '.ce-preview{padding:8px 10px;border-radius:9px;background:#f1eee6;font-size:.88rem}.ce-preview .morph-link{display:inline-block;padding:1px 6px;border-radius:999px;border:1px solid var(--line);text-decoration:none;font-family:ui-monospace,monospace;font-size:.78rem;background:#fff}',
    '.ce-linkrow{display:flex;gap:12px;flex-wrap:wrap;align-items:center;font-size:.82rem}',
    '.ce-linkrow button{border:0;background:none;padding:0;color:var(--accent);cursor:pointer;font:inherit;font-weight:600}',
    '.ce-error{padding:9px 12px;border-radius:9px;background:#fdecea;color:#912018;font-size:.88rem}',
    '.ce-help{color:var(--muted);font-size:.88rem;margin:0}.ce-help ol{margin:6px 0 0;padding-left:20px}',
    '.ce-toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:9999;padding:10px 16px;border-radius:12px;background:#25231f;color:#fff;font-size:.9rem;box-shadow:0 10px 30px rgba(0,0,0,.25)}',
    '.ce-card-actions{display:flex;gap:6px;margin-top:10px}',
    '@media(max-width:560px){.ce-seg{grid-template-columns:minmax(0,1fr) auto auto auto}.ce-seg .ce-link{display:none}}'
  ].join('\n');

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      var v = attrs[k];
      if (k === 'class') n.className = v; else if (k === 'text') n.textContent = v; else if (k === 'html') n.innerHTML = v;
      else if (k.slice(0, 2) === 'on') n.addEventListener(k.slice(2), v); else if (v !== false && v != null) n.setAttribute(k, v === true ? '' : v);
    });
    (kids || []).forEach(function (c) { if (c != null) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function toast(msg, ms) {
    var t = el('div', { class: 'ce-toast', text: msg }); document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, ms || 3500);
  }
  var dlCount = 0;
  function datalist(options) {
    var id = 'ce-dl-' + (++dlCount), dl = el('datalist', { id: id });
    options.forEach(function (o) { dl.appendChild(el('option', { value: o })); });
    document.body.appendChild(dl); return id;
  }
  function field(label, input, hint) { return el('label', { class: 'ce-field' }, [el('span', { text: label }), input, hint ? el('small', { text: hint }) : null]); }
  function textInput(value, attrs) { return el('input', Object.assign({ type: 'text', value: value || '', spellcheck: 'false', autocomplete: 'off' }, attrs || {})); }
  function textArea(value, attrs) { var t = el('textarea', attrs || {}); t.value = value || ''; return t; }

  function chipInput(values, suggestions, placeholder) {
    var list = (values || []).slice(), wrap = el('div', { class: 'ce-chips' });
    var input = el('input', { list: datalist(suggestions || []), placeholder: placeholder || '', autocomplete: 'off', spellcheck: 'false' });
    function render() {
      wrap.querySelectorAll('.ce-chip').forEach(function (c) { c.remove(); });
      list.forEach(function (v, i) {
        wrap.insertBefore(el('span', { class: 'ce-chip' }, [v, el('button', { type: 'button', title: 'Quitar', text: '×', onclick: function () { list.splice(i, 1); render(); } })]), input);
      });
    }
    function commit() {
      input.value.split(',').map(function (x) { return x.trim(); }).filter(Boolean).forEach(function (v) { if (list.indexOf(v) < 0) list.push(v); });
      input.value = ''; render();
    }
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); commit(); }
      else if (e.key === 'Backspace' && !input.value && list.length) { list.pop(); render(); }
    });
    input.addEventListener('change', function () { if (suggestions && suggestions.indexOf(input.value) >= 0) commit(); });
    input.addEventListener('blur', commit);
    wrap.appendChild(input); render();
    wrap.addEventListener('click', function (e) { if (e.target === wrap) input.focus(); });
    return { el: wrap, get: function () { commit(); return list.slice(); } };
  }


  /* Selector híbrido de iconos: catálogo local + búsqueda + emoji Unicode pegado. */
  var EMOJI_GROUPS = [
    ['Frecuentes', [
      ['⛺','acampar tienda campaña'],['🏕️','campamento camping'],['🌳','árbol bosque'],['🏠','casa hogar'],
      ['📚','libros lectura estudio'],['❤️','amor corazón'],['⭐','estrella'],['🌍','mundo tierra'],
      ['🔥','fuego quemar'],['💧','agua gota'],['☀️','sol día'],['🌙','luna noche'],
      ['🧠','mente cerebro'],['🛠️','herramientas trabajo'],['🚶','caminar andar'],['🧭','brújula orientación']
    ]],
    ['Naturaleza y clima', [
      ['🌲','pino conífera bosque'],['🌴','palmera tropical'],['🌿','hierba planta'],['🍀','trébol suerte'],
      ['🌸','flor rosa'],['🌻','girasol flor'],['🍄','hongo seta'],['🌾','espiga cereal'],
      ['🍎','manzana fruta'],['🍇','uva fruta'],['🥕','zanahoria verdura'],['🌱','brote crecer'],
      ['🌊','ola mar agua'],['🏞️','paisaje naturaleza'],['⛰️','montaña pico'],['🏜️','desierto arena'],
      ['🌋','volcán lava'],['🪨','piedra roca'],['🌧️','lluvia nube'],['⛈️','tormenta trueno'],
      ['❄️','nieve frío'],['🌈','arcoíris colores'],['🌬️','viento aire'],['🌫️','niebla bruma']
    ]],
    ['Animales', [
      ['🐕','perro'],['🐈','gato'],['🐺','lobo'],['🦊','zorro'],['🐻','oso'],['🦁','león'],
      ['🐎','caballo'],['🐄','vaca buey'],['🐑','oveja'],['🐖','cerdo puerco'],['🐇','conejo'],
      ['🦅','águila ave'],['🐦','pájaro ave'],['🦆','pato'],['🐝','abeja insecto'],
      ['🦋','mariposa'],['🐜','hormiga'],['🐍','serpiente'],['🐟','pez pescado'],
      ['🐬','delfín'],['🦀','cangrejo'],['🐸','rana']
    ]],
    ['Personas y cuerpo', [
      ['🧍','persona estar de pie'],['👨','hombre'],['👩','mujer'],['👶','bebé niño'],
      ['👨‍👩‍👧','familia'],['🧑‍🤝‍🧑','personas pareja'],['👁️','ojo ver'],['👂','oreja oído'],
      ['👃','nariz olfato'],['👄','boca labios'],['🦷','diente'],['🦴','hueso'],
      ['✋','mano palma'],['🦶','pie'],['💪','brazo fuerza músculo'],['🫀','corazón órgano'],
      ['🩸','sangre'],['🧬','genética ADN'],['😴','dormir sueño'],['😊','alegría sonrisa'],
      ['😢','tristeza llanto'],['😠','ira enojo'],['🤔','pensar reflexión'],['🗣️','hablar voz']
    ]],
    ['Objetos y lugares', [
      ['📖','libro abierto'],['✏️','lápiz escribir'],['🔑','llave'],['🚪','puerta'],
      ['🛏️','cama dormir'],['🪑','silla asiento'],['🏰','castillo fortaleza'],['🏙️','ciudad'],
      ['🏡','vivienda pueblo'],['🌉','puente'],['⛵','barco navegar'],['🚗','auto coche'],
      ['🚆','tren transporte'],['✈️','avión viaje'],['🗺️','mapa'],['🔭','telescopio'],
      ['🔬','microscopio ciencia'],['⚖️','balanza justicia'],['🛡️','escudo proteger'],['⚔️','espadas combate'],
      ['💡','luz idea'],['⚙️','engranaje mecanismo'],['📦','paquete caja'],['💎','gema cristal']
    ]],
    ['Acciones y símbolos', [
      ['🏃','correr movimiento'],['🏊','nadar agua'],['🧗','escalar trepar'],['🚴','bicicleta ciclismo'],
      ['🪓','hacha cortar'],['🔨','martillo construir'],['🧵','hilo coser'],['🎨','pintura arte'],
      ['🎭','teatro máscaras'],['🎶','música cantar'],['⚽','fútbol deporte'],['🎯','objetivo blanco meta'],
      ['🎁','regalo dar'],['🤝','acuerdo saludo'],['💬','diálogo conversación'],['✅','correcto sí'],
      ['❌','incorrecto no'],['❓','interrogación pregunta'],['⚠️','advertencia peligro'],
      ['♻️','reciclaje ciclo'],['🕰️','reloj tiempo'],['♾️','infinito'],['➕','más suma'],
      ['➖','menos resta'],['🔄','girar volver'],['⬆️','arriba'],['⬇️','abajo']
    ]]
  ];
  function validEmoji(value) {
    var s = String(value || '').trim();
    if (!s) return true;
    if (s.length > 64 || !/[\p{Extended_Pictographic}\p{Regional_Indicator}\u20E3]/u.test(s)) return false;
    if (typeof Intl !== 'undefined' && Intl.Segmenter) {
      return Array.from(new Intl.Segmenter('es', { granularity: 'grapheme' }).segment(s)).length === 1;
    }
    return true;
  }
  function emojiPicker(value) {
    var chosen = String(value || '').trim();
    var holder = el('div', { class: 'ce-emoji-picker' });
    var trigger = el('button', { type: 'button', class: 'ce-emoji-trigger',
      title: 'Elegir emoji del vocablo', 'aria-label': 'Elegir emoji del vocablo', 'aria-expanded': 'false' });
    var panel = el('div', { class: 'ce-emoji-panel', hidden: true });
    var search = textInput('', { placeholder: 'Buscar emoji (árbol, casa, fuego…)', 'aria-label': 'Buscar emoji' });
    var results = el('div', { class: 'ce-emoji-results' });
    var paste = textInput('', { placeholder: 'Pega cualquier emoji', maxlength: '64', 'aria-label': 'Pegar otro emoji' });
    var help = el('small', { class: 'ce-emoji-empty', text: 'También puedes pegar un emoji que no esté en el catálogo.' });
    function fold(t) {
      return String(t || '').toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }
    function open(show) {
      panel.hidden = !show;
      trigger.setAttribute('aria-expanded', String(show));
      if (show) { renderResults(); search.focus(); }
    }
    function select(value) {
      var emoji = String(value || '').trim();
      if (!validEmoji(emoji)) { help.textContent = 'Introduce un único emoji válido.'; return; }
      chosen = emoji;
      trigger.textContent = chosen || '＋';
      trigger.title = chosen ? 'Cambiar o quitar emoji' : 'Elegir emoji del vocablo';
      paste.value = '';
      help.textContent = 'También puedes pegar un emoji que no esté en el catálogo.';
      open(false);
    }
    function renderResults() {
      results.innerHTML = '';
      var q = fold(search.value), any = false;
      EMOJI_GROUPS.forEach(function (group) {
        var items = group[1].filter(function (item) {
          return !q || fold(item[1]).includes(q) || item[0].includes(q);
        });
        if (!items.length) return;
        any = true;
        var grid = el('div', { class: 'ce-emoji-grid' });
        items.forEach(function (item) {
          grid.appendChild(el('button', { type: 'button', class: 'ce-emoji-option',
            text: item[0], title: item[1], 'aria-label': item[1],
            onclick: function () { select(item[0]); } }));
        });
        results.appendChild(el('section', { class: 'ce-emoji-group' },
          [el('span', { class: 'ce-emoji-group-title', text: group[0] }), grid]));
      });
      if (!any) results.appendChild(el('div', { class: 'ce-emoji-empty',
        text: 'No se encontraron emojis. Puedes pegar otro abajo.' }));
    }
    trigger.textContent = chosen || '＋';
    trigger.addEventListener('click', function () { open(panel.hidden); });
    search.addEventListener('input', renderResults);
    search.addEventListener('keydown', function (e) { if (e.key === 'Enter') e.preventDefault(); });
    paste.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); select(paste.value); }
    });
    panel.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.stopPropagation(); open(false); trigger.focus(); }
    });
    var apply = el('button', { type: 'button', class: 'ce-btn small', text: 'Usar',
      onclick: function () { select(paste.value); } });
    var remove = el('button', { type: 'button', class: 'ce-btn small', text: 'Quitar icono',
      onclick: function () { select(''); } });
    panel.appendChild(search);
    panel.appendChild(results);
    panel.appendChild(el('div', { class: 'ce-emoji-paste' }, [paste, apply]));
    panel.appendChild(remove);
    panel.appendChild(help);
    holder.appendChild(trigger);
    holder.appendChild(panel);
    function onOutside(event) {
      if (!holder.isConnected) { document.removeEventListener('pointerdown', onOutside, true); return; }
      if (!holder.contains(event.target)) open(false);
    }
    document.addEventListener('pointerdown', onOutside, true);
    return { el: holder, get: function () { return chosen; } };
  }

  /* Constructor de análisis: segmentos enlazables a morfemas, raíces y vocablos, o HTML libre. */
  function analysisEditor(word, defaultFirst, idx) {
    var refOpts = [], refInfo = {};
    (idx.morphemes || []).forEach(function (m) { var l = bare(m.form); refInfo[m.id] = { label: l, gloss: m.gloss, kind: 'morfema' }; refOpts.push(l + '  ·  ' + m.gloss + '  [' + m.id + ']'); });
    (idx.roots || []).forEach(function (r) { var l = rootLabel(r.form); refInfo[r.id] = { label: l, gloss: r.gloss, kind: 'raíz' }; refOpts.push(l + '  ·  ' + r.gloss + '  [' + r.id + ']'); });
    (idx.words || []).forEach(function (w) { if (word && w.id === word.id) return; refInfo[w.id] = { label: w.form, gloss: w.gloss, kind: 'vocablo' }; refOpts.push(w.form + '  ·  ' + w.gloss + '  ·  vocablo [' + w.id + ']'); });
    var dl = datalist(refOpts);
    /* Enlace automático: si el texto escrito coincide con la forma de un morfema, se enlaza sin tener que
       elegirlo de la lista (solo morfemas; raíces y vocablos se seleccionan explícitamente). Primero coincidencia exacta (con guiones), luego sin guiones ni mayúsculas. */
    function norm(t, keepHyphen) { t = String(t || '').trim().toLocaleLowerCase('es'); return keepHyphen ? t : t.replace(/-/g, ''); }
    function candidates(text) {
      if (!norm(text)) return [];
      var ids = Object.keys(refInfo).filter(function (id) { return refInfo[id].kind === 'morfema'; }), exact = ids.filter(function (id) { return norm(refInfo[id].label, true) === norm(text, true); });
      return exact.length ? exact : ids.filter(function (id) { return norm(refInfo[id].label) === norm(text); });
    }
    var orig = word ? { analysis_html: word.analysis_html || '', analysis_text: word.analysis_text || '', refs: word.refs || [] } : null;
    var parsed = orig ? parseAnalysis(orig.analysis_html) : { segs: defaultFirst ? [{ ref: null, text: defaultFirst, q: false }] : [], pend: false };
    var mode = parsed && (!orig || segsHTML(parsed.segs, parsed.pend) === orig.analysis_html) ? 'seg' : 'html';
    var segs = parsed ? parsed.segs : [], pend = parsed ? parsed.pend : false, dirty = false;
    var box = el('div', { class: 'ce-field' }), segWrap = el('div', { class: 'ce-segs' }), preview = el('div', { class: 'ce-preview' });
    var htmlBox = textArea(orig ? orig.analysis_html : '', { class: 'ce-mono', rows: 3 });
    var pendBox = el('input', { type: 'checkbox' }); pendBox.checked = pend;
    pendBox.addEventListener('change', function () { pend = pendBox.checked; dirty = true; update(); });
    htmlBox.addEventListener('input', function () { dirty = true; update(); });
    function currentHTML() { return mode === 'seg' ? segsHTML(segs, pend) : htmlBox.value.trim(); }
    function update() { var h = currentHTML(); preview.innerHTML = h || '<span style="color:var(--muted)">(sin análisis)</span>'; }
    function segRow(s, i) {
      var inp = textInput(s.text, { list: dl, class: 'ce-mono', placeholder: 'Raíz, morfema, vocablo o texto' });
      var link = el('span', { class: 'ce-link' + (s.ref ? ' linked' : '') });
      var pick = el('select', { class: 'ce-pick', hidden: true, title: 'Varias coincidencias: elige a cuál enlazar' });
      pick.addEventListener('change', function () {
        if (pick.value) { s.ref = pick.value; s.text = refInfo[s.ref].label; inp.value = s.text; }
        else s.ref = null;
        dirty = true; showLink(); update();
      });
      function showLink() {
        link.className = 'ce-link' + (s.ref ? ' linked' : '');
        link.textContent = s.ref ? '→ ' + (refInfo[s.ref] ? refInfo[s.ref].kind + ': ' + refInfo[s.ref].gloss : s.ref) : 'texto';
        link.title = s.ref || 'Segmento sin enlace';
        inp.classList.toggle('ce-linked', !!s.ref);
        var c = s.ref ? [] : candidates(s.text);
        pick.hidden = c.length < 2; link.hidden = c.length >= 2;
        if (c.length >= 2) {
          pick.innerHTML = '';
          pick.appendChild(el('option', { value: '', text: 'texto (sin enlace) · ' + c.length + ' coincidencias' }));
          c.forEach(function (id) { pick.appendChild(el('option', { value: id, text: refInfo[id].kind + ': ' + refInfo[id].label + ' · ' + refInfo[id].gloss })); });
        }
      }
      function autoLink() {
        if (s.ref) return;
        var c = candidates(s.text);
        if (c.length === 1) { s.ref = c[0]; s.text = refInfo[c[0]].label; inp.value = s.text; dirty = true; update(); }
        showLink();
      }
      inp.addEventListener('change', autoLink);
      inp.addEventListener('input', function () {
        var m = inp.value.match(/\[([^\]]+)\]\s*$/);
        if (m && refInfo[m[1]]) { s.ref = m[1]; s.text = refInfo[m[1]].label; inp.value = s.text; }
        else {
          s.text = inp.value;
          if (s.ref && (!refInfo[s.ref] || refInfo[s.ref].label !== s.text.trim())) s.ref = null;
        }
        dirty = true; showLink(); update();
      });
      var q = el('input', { type: 'checkbox', title: 'Dudoso (?)' }); q.checked = s.q;
      q.addEventListener('change', function () { s.q = q.checked; dirty = true; update(); });
      showLink();
      return el('div', { class: 'ce-seg' }, [inp, el('span', {}, [link, pick]), el('label', {}, [q, ' ?']),
        el('button', { type: 'button', class: 'ce-ico', title: 'Subir', text: '↑', onclick: function () { if (i > 0) { segs.splice(i - 1, 0, segs.splice(i, 1)[0]); dirty = true; render(); } } }),
        el('button', { type: 'button', class: 'ce-ico', title: 'Quitar', text: '×', onclick: function () { segs.splice(i, 1); dirty = true; render(); } })]);
    }
    function render() {
      box.innerHTML = '';
      box.appendChild(el('span', { text: 'Análisis' }));
      if (mode === 'seg') {
        segWrap.innerHTML = ''; segs.forEach(function (s, i) { segWrap.appendChild(segRow(s, i)); });
        box.appendChild(segWrap);
        box.appendChild(el('div', { class: 'ce-linkrow' }, [
          el('button', { type: 'button', text: '+ segmento', onclick: function () { segs.push({ ref: null, text: '', q: false }); dirty = true; render(); var ins = segWrap.querySelectorAll('input[type=text]'); if (ins.length) ins[ins.length - 1].focus(); } }),
          el('label', {}, [pendBox, ' (pendiente)']),
          el('button', { type: 'button', text: 'Editar como HTML', onclick: function () { htmlBox.value = segsHTML(segs, pend); mode = 'html'; render(); } })
        ]));
        box.appendChild(el('small', { text: 'Escribe un morfema (p. ej. -AR) y se enlaza solo al salir del campo; para raíces y vocablos, elige la opción de la lista (con identificador). Si hay varias coincidencias aparece un selector. Lo demás queda como texto.' }));
      } else {
        box.appendChild(htmlBox);
        box.appendChild(el('div', { class: 'ce-linkrow' }, [
          el('button', { type: 'button', text: 'Volver a segmentos', onclick: function () {
            var p = parseAnalysis(htmlBox.value.trim());
            if (!p) { alert('Este análisis tiene una estructura que el editor de segmentos no reproduce. Sigue en modo HTML.'); return; }
            segs = p.segs; pend = p.pend; pendBox.checked = pend; mode = 'seg'; render();
          } })
        ]));
        box.appendChild(el('small', { text: 'Enlaces: <a class="morph-link" href="#morph-…">-X</a>, <a class="morph-link" href="#root-…">RAÍZ</a> o <a class="morph-link" href="#lexeme-…">vocablo</a>. Texto y referencias se derivan solos.' }));
      }
      box.appendChild(preview); update();
    }
    render();
    return { el: box, get: function () { return (!dirty && orig) ? orig : analysisFromHTML(currentHTML()); } };
  }

  /* Diálogo genérico */
  function dialog(title, bodyNodes, opts) {
    var errBox = el('div', { class: 'ce-error', hidden: true });
    var save = el('button', { type: 'submit', class: 'ce-btn primary', text: opts.saveLabel || 'Guardar' });
    var foot = [];
    if (opts.onDelete) foot.push(el('button', { type: 'button', class: 'ce-btn danger', text: opts.deleteLabel || 'Eliminar', onclick: function () { run(opts.onDelete); } }));
    foot.push(el('span', { class: 'ce-spacer' }), el('button', { type: 'button', class: 'ce-btn', text: 'Cancelar', onclick: function () { close(); } }));
    if (opts.onSave) foot.push(save);
    var form = el('form', { method: 'dialog' }, [
      el('div', { class: 'ce-head' }, [el('h2', { text: title }), el('button', { type: 'button', class: 'ce-x', 'aria-label': 'Cerrar', text: '×', onclick: function () { close(); } })]),
      el('div', { class: 'ce-body' }, [errBox].concat(bodyNodes)),
      el('div', { class: 'ce-foot' }, foot)
    ]);
    var d = el('dialog', { class: 'ce-dialog' }, [form]);
    function close() { d.close(); d.remove(); }
    function run(fn) {
      errBox.hidden = true;
      var btns = d.querySelectorAll('.ce-foot button'); btns.forEach(function (b) { b.disabled = true; });
      save.textContent = 'Guardando…';
      Promise.resolve().then(fn).then(function (res) {
        if (res === false) return;
        close();
        if (res && res.sha) toast('Guardado · commit ' + res.sha.slice(0, 7));
        if (res && res.after) setTimeout(res.after, 700);
      }).catch(function (err) {
        console.error(err);
        errBox.textContent = err.status === 401 || err.status === 403 || err.status === 404
          ? 'GitHub rechazó la escritura (' + err.status + '). Revisa que el token tenga acceso a lucumur/Conlang con permiso Contents: lectura y escritura.'
          : err.message;
        errBox.hidden = false; errBox.scrollIntoView({ block: 'nearest' });
      }).then(function () { btns.forEach(function (b) { b.disabled = false; }); save.textContent = opts.saveLabel || 'Guardar'; });
    }
    form.addEventListener('submit', function (e) { e.preventDefault(); if (opts.onSave) run(opts.onSave); });
    document.body.appendChild(d); d.showModal();
    return { close: close, error: function (m) { errBox.textContent = m; errBox.hidden = false; } };
  }
  function reload() { location.reload(); }
  function goRoot(id) { return function () { location.assign('raiz.html?id=' + encodeURIComponent(id)); }; }

  /* ---------- Token y activación ---------- */
  function tokenDialog() {
    var inp = el('input', { type: 'password', autocomplete: 'off', placeholder: 'github_pat_…', class: 'ce-mono' });
    var on = editOn();
    var body = [
      el('div', { class: 'ce-help', html:
        'El modo edición guarda cada cambio como un commit en <code>lucumur/Conlang</code>. Necesita un token personal de GitHub, que se guarda solo en este navegador.' +
        '<ol><li>Abre <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noopener">GitHub → Fine-grained token</a>.</li>' +
        '<li>Repository access: <strong>Only select repositories</strong> → <code>Conlang</code>.</li>' +
        '<li>Permissions → Repository → <strong>Contents: Read and write</strong>.</li>' +
        '<li>Genera el token y pégalo aquí.</li></ol>' }),
      field('Token', inp)
    ];
    if (token()) body.unshift(el('div', { class: 'ce-help', html: 'Ya hay un token guardado en este navegador' + (on ? ' y el modo edición está <strong>activo</strong>.' : '.') }));
    dialog(on ? 'Modo edición' : 'Activar modo edición', body, {
      saveLabel: on ? 'Cambiar token' : 'Activar',
      deleteLabel: on ? 'Salir del modo edición' : 'Olvidar token',
      onDelete: token() ? function () {
        if (on) ls(EK, null); else ls(TK, null);
        return { after: reload };
      } : null,
      onSave: function () {
        var t = inp.value.trim() || token();
        if (!t) fail('Pega un token.');
        var prev = token(); ls(TK, t);
        return gh(RP).then(function (repo) {
          ls(EK, '1'); toast('Modo edición activo'); return { after: reload };
        }, function (err) { if (prev) ls(TK, prev); else ls(TK, null); fail('El token no funciona para lucumur/Conlang (' + err.message + ').'); });
      }
    });
  }

  /* ---------- Raíces ---------- */
  function rootDialog(rootId) {
    var isNew = !rootId;
    return Promise.all([loadIndex(), isNew ? null : loadIndex().then(function (idx) {
      var meta = idx.roots.find(function (r) { return r.id === rootId; });
      if (!meta) throw Error('Raíz no encontrada en el índice: ' + rootId);
      return readJSON('lexico/' + meta.key + '.json', currentRef()).then(function (d) { return { meta: meta, entry: d.entries.find(function (e) { return e.id === rootId; }) }; });
    })]).then(function (r) {
      var idx = r[0], cur = r[1] ? r[1].entry : null;
      var extraTags = ['Bas','Part.','Sono','formal','Mundial','arcaico','onomato','nom','Esper','Neo'];
      var relationOf = function(t){return ROOT_RELATION.some(function(l){return l.toLowerCase()===(t.class||'').toLowerCase();});};
      var etymOf = function(t){return EXTERNAL_ETYM.some(function(l){return l.toLowerCase()===(t.class||'').toLowerCase();});};
      var fForm = textInput(cur ? cur.form : '*', { class: 'ce-mono', required: true, placeholder: '*RAÍZ-' });
      var fGloss = textInput(cur ? cur.gloss : '', { required: true });
      var fEt = textArea(cur ? cur.etymology || '' : '', { rows: 3, placeholder: '< Eo. … , del lat. …' });
      var fNotes = textArea(cur ? (cur.notes || []).join('\n') : '', { rows: 2, placeholder: 'Una nota por línea' });
      var currentTags = cur ? cur.tags || [] : [];
      var fRelation = chipInput(labels(currentTags.filter(relationOf)), ROOT_RELATION, 'Nat-Plen, Nat-Mod, Nat-Red, Nova');
      var fEtym = chipInput(labels(currentTags.filter(etymOf)), EXTERNAL_ETYM, 'Latin, Germanico, Frances…');
      var fTags = chipInput(labels(currentTags.filter(function(t){return !relationOf(t)&&!etymOf(t); })), extraTags, 'Otras etiquetas (si proceden)');
      var body = [el('div', { class: 'ce-row' }, [field('Forma', fForm, 'Con asterisco y guiones: *ĴAR-, *MA-J'), field('Glosa', fGloss)]),
        field('Etimología', fEt), field('Notas', fNotes),
        field('Relación con esperanto', fRelation.el, 'Normalmente una sola clasificación. La franja lateral representa esta categoría.'),
        field('Procedencia etimológica externa', fEtym.el, 'Se pueden indicar varias lenguas de origen.'),
        field('Otras etiquetas', fTags.el, 'Anotaciones heredadas que no son clasificación esperántica ni lengua natural.')];
      if (cur && currentTags.filter(relationOf).length>1) body.push(el('small', { class: 'ce-error', text: 'Clasificación múltiple: esta raíz tiene más de una relación con esperanto. Revísala cuando corresponda.' }));
      if (cur) body.push(el('small', { class: 'ce-help', text: 'Identificador: ' + cur.id + ' (no cambia aunque cambie la forma)' }));
      dialog(isNew ? 'Nueva raíz' : 'Editar raíz ' + cur.form, body, {
        onDelete: isNew ? null : function () {
          var used = idx.words.filter(function (w) { return w.refs.indexOf(rootId) >= 0 && w.root_id !== rootId; }).length;
          var n = (cur.words || []).length;
          if (!confirm('¿Eliminar la raíz ' + cur.form + (n ? ' y sus ' + n + ' vocablos' : '') + '?' + (used ? '\n\nOJO: ' + used + ' vocablos de otras raíces la citan en su análisis.' : ''))) return false;
          return transact(function (ctx) {
            var meta = r[1].meta, path = 'lexico/' + meta.key + '.json';
            return ctx.read(path).then(function (d) {
              var i = d.entries.findIndex(function (e) { return e.id === rootId; });
              if (i < 0) fail('La raíz ya no existe.');
              d.entries.splice(i, 1);
              var files = {}; files[path] = d;
              return { files: files, message: 'Raíz: eliminar ' + cur.form + ' «' + cur.gloss + '»', after: function () { location.assign('lexico.html#sec-' + meta.key); } };
            });
          });
        },
        onSave: function () {
          var form = fForm.value.trim(), gloss = fGloss.value.trim();
          if (!/^\*?\S/.test(form) || form === '*') fail('Escribe la forma de la raíz.');
          if (form[0] !== '*') form = '*' + form;
          if (!gloss) fail('Escribe la glosa.');
          var L = letterOf(form); if (!L) fail('La inicial de ' + form + ' no corresponde a ninguna letra del léxico.');
          var et = fEt.value.trim() || null, notes = lines(fNotes.value), tagLabels = fRelation.get().concat(fEtym.get(),fTags.get());
          return transact(function (ctx) {
            return ctx.read('lexico/index.json').then(function (cidx) {
              var files = {};
              if (isNew) {
                var path = 'lexico/' + L.key + '.json';
                return ctx.read(path).then(function (d) {
                  var id = uniqueId('root-' + slug(rootLabel(form)), new Set(cidx.roots.map(function (x) { return x.id; }).concat(d.entries.map(function (x) { return x.id; }))));
                  insertSorted(d.entries, { id: id, form: form, gloss: gloss, tags: tagsFrom(tagLabels, []), letter: L.letter, section: 'sec-' + L.key,
                    etymology: et, notes: notes, row_class: '', words: [] }, function (x) { return x.form || ''; });
                  files[path] = d;
                  return { files: files, message: 'Raíz: añadir ' + form + ' «' + gloss + '»', after: goRoot(id) };
                });
              }
              var meta = cidx.roots.find(function (x) { return x.id === rootId; });
              if (!meta) fail('La raíz ya no existe en el índice.');
              var oldPath = 'lexico/' + meta.key + '.json', newPath = 'lexico/' + L.key + '.json';
              return Promise.all([ctx.read(oldPath), ctx.read(newPath)]).then(function (ds) {
                var d = ds[0], i = d.entries.findIndex(function (x) { return x.id === rootId; });
                if (i < 0) fail('La raíz ya no existe.');
                var e = d.entries[i], before = JSON.stringify(e);
                e.form = form; e.gloss = gloss; e.etymology = et; e.notes = notes; e.tags = tagsFrom(tagLabels, e.tags);
                var msg = 'Raíz: editar ' + form;
                if (L.key !== meta.key) {
                  d.entries.splice(i, 1); e.letter = L.letter; e.section = 'sec-' + L.key;
                  insertSorted(ds[1].entries, e, function (x) { return x.form || ''; });
                  files[newPath] = ds[1]; msg = 'Raíz: mover ' + cur.form + ' → ' + form + ' (letra ' + L.letter + ')';
                } else if (JSON.stringify(e) === before) fail('No hay cambios que guardar.');
                files[oldPath] = d;
                return { files: files, message: msg, after: reload };
              });
            });
          });
        }
      });
    });
  }

  /* ---------- Vocablos ---------- */
  function wordDialog(rootId, wordId) {
    var isNew = !wordId;
    return loadIndex().then(function (idx) {
      var meta = rootId ? idx.roots.find(function (r) { return r.id === rootId; }) : null;
      var load = meta ? readJSON('lexico/' + meta.key + '.json', currentRef()) : Promise.resolve(null);
      return load.then(function (d) {
        var root = d ? d.entries.find(function (e) { return e.id === rootId; }) : null;
        var w = root && wordId ? (root.words || []).find(function (x) { return x.id === wordId; }) : null;
        if (wordId && !w) throw Error('Vocablo no encontrado: ' + wordId);
        var fields = {}, wtags = {};
        idx.words.forEach(function (x) { (x.semantic_fields || []).forEach(function (f) { fields[f] = 1; }); (x.tags || []).forEach(function (t) { wtags[t] = 1; }); });
        var rootOpts = idx.roots.map(function (r) { return r.form + '  ·  ' + r.gloss + '  [' + r.id + ']'; });
        var chosenRoot = meta, fRoot = null;
        var fForm = textInput(w ? w.form : '', { class: 'ce-mono', required: true });
        var fEmoji = emojiPicker(w ? w.emoji : '');
        var fGloss = textInput(w ? w.gloss : '', { required: true });
        var an = analysisEditor(w, root ? rootLabel(root.form) : '', idx), anSlot = el('div', {}, [an.el]);
        var fSem = chipInput(w ? w.semantic_fields || [] : [], Object.keys(fields).sort(coll.compare), 'Campo semántico (Enter para añadir)');
        var fTags = chipInput(w ? labels(w.tags) : [], Object.keys(wtags).sort(coll.compare), 'Etiqueta (Nominal A, Verbal OS…)');
        var fNotes = textArea(w ? (w.notes || []).join('\n') : '', { rows: 2, placeholder: 'Una nota por línea (p. ej. Pendiente: …)' });
        var body = [];
        if (!meta) {
          fRoot = textInput('', { list: datalist(rootOpts), class: 'ce-mono', placeholder: 'Busca la raíz: *ĴAR-…', required: true });
          fRoot.addEventListener('change', function () {
            var m = fRoot.value.match(/\[([^\]]+)\]\s*$/), r = m && idx.roots.find(function (x) { return x.id === m[1]; });
            chosenRoot = r || null;
            if (r) { fRoot.value = r.form + '  ·  ' + r.gloss + '  [' + r.id + ']'; an = analysisEditor(null, rootLabel(r.form), idx); anSlot.innerHTML = ''; anSlot.appendChild(an.el); }
          });
          body.push(field('Raíz', fRoot, 'Elige de la lista.'));
        }
        body.push(el('div', { class: 'ce-row' }, [field('Forma', el('div', { class: 'ce-word-form-row' }, [fEmoji.el, fForm]), 'Pulsa el icono para elegir, pegar o quitar un emoji.'), field('Glosa', fGloss)]), anSlot,
          field('Campos semánticos', fSem.el), field('Etiquetas', fTags.el), field('Notas', fNotes));
        dialog(isNew ? 'Nuevo vocablo' + (root ? ' en ' + root.form : '') : 'Editar vocablo ' + w.form, body, {
          onDelete: isNew ? null : function () {
            var used = idx.words.filter(function (x) { return x.refs.indexOf(wordId) >= 0; }).length;
            if (!confirm('¿Eliminar el vocablo ' + w.form + ' «' + w.gloss + '»?' + (used ? '\n\nOJO: ' + used + ' vocablos lo citan.' : ''))) return false;
            return transact(function (ctx) {
              return ctx.read('lexico/index.json').then(function (cidx) {
                var m = cidx.roots.find(function (x) { return x.id === rootId; }), path = 'lexico/' + m.key + '.json';
                return ctx.read(path).then(function (dd) {
                  var e = dd.entries.find(function (x) { return x.id === rootId; }), i = (e.words || []).findIndex(function (x) { return x.id === wordId; });
                  if (i < 0) fail('El vocablo ya no existe.');
                  e.words.splice(i, 1);
                  var files = {}; files[path] = dd;
                  return { files: files, message: 'Vocablo: eliminar ' + w.form + ' (' + e.form + ')', after: reload };
                });
              });
            });
          },
          onSave: function () {
            if (!chosenRoot) fail('Elige la raíz de la lista.');
            var form = fForm.value.trim(), gloss = fGloss.value.trim();
            if (!form) fail('Escribe la forma del vocablo.');
            if (!gloss) fail('Escribe la glosa.');
            var emoji = fEmoji.get();
            if (!validEmoji(emoji)) fail('El icono debe ser un único emoji Unicode.');
            var a = an.get(), sem = fSem.get(), tagLabels = fTags.get(), notes = lines(fNotes.value), rid = chosenRoot.id;
            return transact(function (ctx) {
              return ctx.read('lexico/index.json').then(function (cidx) {
                var m = cidx.roots.find(function (x) { return x.id === rid; });
                if (!m) fail('La raíz ya no existe.');
                var path = 'lexico/' + m.key + '.json';
                return ctx.read(path).then(function (dd) {
                  var e = dd.entries.find(function (x) { return x.id === rid; });
                  if (!e) fail('La raíz ya no existe.');
                  e.words = e.words || [];
                  var files = {}; files[path] = dd;
                  if (isNew) {
                    var taken = new Set(cidx.words.map(function (x) { return x.id; }).concat(e.words.map(function (x) { return x.id; })));
                    var nw = { id: uniqueId('lexeme-' + slug(form), taken), form: form, gloss: gloss,
                      analysis_html: a.analysis_html, analysis_text: a.analysis_text, refs: a.refs,
                      tags: tagsFrom(tagLabels, []), semantic_fields: sem, notes: notes };
                    if (emoji) nw.emoji = emoji;
                    e.words.push(nw);
                    return { files: files, message: 'Vocablo: añadir ' + form + ' «' + gloss + '» (' + e.form + ')', after: rootId ? reload : goRoot(rid) };
                  }
                  var x = e.words.find(function (y) { return y.id === wordId; });
                  if (!x) fail('El vocablo ya no existe.');
                  var before = JSON.stringify(x);
                  x.form = form; x.gloss = gloss;
                  x.analysis_html = a.analysis_html; x.analysis_text = a.analysis_text; x.refs = a.refs;
                  x.tags = tagsFrom(tagLabels, x.tags); x.semantic_fields = sem; x.notes = notes;
                  if (emoji) x.emoji = emoji; else delete x.emoji;
                  if (JSON.stringify(x) === before) fail('No hay cambios que guardar.');
                  return { files: files, message: 'Vocablo: editar ' + form + ' (' + e.form + ')', after: reload };
                });
              });
            });
          }
        });
      });
    });
  }

  /* ---------- Morfemas ---------- */
  function morphDialog(morphId) {
    var isNew = !morphId;
    return Promise.all([loadIndex(), readJSON('lexico/morphemes.json', currentRef())]).then(function (r) {
      var idx = r[0], cur = isNew ? null : r[1].morphemes.find(function (m) { return m.id === morphId; });
      if (!isNew && !cur) throw Error('Morfema no encontrado: ' + morphId);
      var tagSugs = {}; r[1].morphemes.forEach(function (m) { labels(m.tags).forEach(function (l) { tagSugs[l] = 1; }); });
      var fForm = textInput(cur ? cur.form : '*-', { class: 'ce-mono', required: true });
      var fGloss = textInput(cur ? cur.gloss : '', { required: true });
      var fEt = textArea(cur ? cur.etymology || '' : '', { rows: 2 });
      var fNotes = textArea(cur ? (cur.notes || []).join('\n') : '', { rows: 3, placeholder: 'Una nota por línea' });
      var fTags = chipInput(cur ? labels(cur.tags) : ['sufijo'], Object.keys(tagSugs).sort(coll.compare), 'sufijo, prefijo, Provisional…');
      var rootById = new Map((idx.roots || []).map(function (root) { return [root.id, root]; }));
      var rootOption = function (root) { return root.form + ' [' + root.id + ']'; };
      var fRootRefs = chipInput((cur && cur.root_refs || []).map(function (id) {
        return rootById.has(id) ? rootOption(rootById.get(id)) : id;
      }), (idx.roots || []).map(rootOption), '*CO-T [root-co-t]');
      function selectedRootRefs() {
        var chosen = fRootRefs.get().map(function (value) {
          var match = value.match(/\[([^\]]+)\]$/);
          var id = match ? match[1] : value.trim();
          if (!rootById.has(id)) fail('Selecciona una raíz existente de la lista: ' + value);
          return id;
        });
        return Array.from(new Set(chosen));
      }
      var used = cur ? idx.words.filter(function (w) { return w.refs.indexOf(morphId) >= 0; }).length : 0;
      var body = [el('div', { class: 'ce-row' }, [field('Forma', fForm, 'Sufijo *-AR, prefijo *TRA-, infijo *-IL-'), field('Glosa', fGloss)]),
        field('Notas', fNotes), field('Etimología', fEt), field('Etiquetas', fTags.el),
        field('Raíces de origen', fRootRefs.el, 'Vincula solo raíces de las que deriva este morfema; selecciona las opciones con identificador.')];
      if (cur) body.push(el('small', { class: 'ce-help', text: 'Identificador: ' + cur.id + ' · usado en ' + used + ' vocablos' }));
      dialog(isNew ? 'Nuevo morfema' : 'Editar morfema ' + cur.form, body, {
        onDelete: isNew ? null : function () {
          if (!confirm('¿Eliminar el morfema ' + cur.form + '?' + (used ? '\n\nOJO: ' + used + ' vocablos lo enlazan en su análisis; esos enlaces quedarán rotos.' : ''))) return false;
          return transact(function (ctx) {
            return ctx.read('lexico/morphemes.json').then(function (md) {
              var i = md.morphemes.findIndex(function (m) { return m.id === morphId; });
              if (i < 0) fail('El morfema ya no existe.');
              md.morphemes.splice(i, 1);
              return { files: { 'lexico/morphemes.json': md }, message: 'Morfema: eliminar ' + cur.form, after: reload };
            });
          });
        },
        onSave: function () {
          var form = fForm.value.trim(), gloss = fGloss.value.trim();
          if (form[0] !== '*') form = '*' + form;
          if (bare(form).replace(/-/g, '') === '') fail('Escribe la forma del morfema.');
          if (!gloss) fail('Escribe la glosa.');
          var L = letterOf(form); if (!L) fail('La inicial de ' + form + ' no corresponde a ninguna letra del léxico.');
          var et = fEt.value.trim() || null, notes = lines(fNotes.value), tagLabels = fTags.get(), rootRefs = selectedRootRefs();
          return transact(function (ctx) {
            return ctx.read('lexico/morphemes.json').then(function (md) {
              var list = md.morphemes, files = { 'lexico/morphemes.json': md };
              if (isNew) {
                var id = uniqueId('morph-' + slug(bare(form)), new Set(list.map(function (m) { return m.id; })));
                var nm = { id: id, form: form, gloss: gloss, tags: tagsFrom(tagLabels, []), letter: L.letter, section: 'sec-' + L.key, etymology: et, notes: notes, row_class: '' };
                if (rootRefs.length) nm.root_refs = rootRefs;
                var last = -1; list.forEach(function (m, i) { if (m.letter === L.letter) last = i; });
                if (last < 0) { var order = LETTER_FILES.map(function (x) { return x[0]; }); list.forEach(function (m, i) { if (order.indexOf(m.letter) < order.indexOf(L.letter)) last = i; }); }
                list.splice(last + 1, 0, nm);
                return { files: files, message: 'Morfema: añadir ' + form + ' «' + gloss + '»', after: function () { location.assign('morfemas.html#' + id); location.reload(); } };
              }
              var m = list.find(function (x) { return x.id === morphId; });
              if (!m) fail('El morfema ya no existe.');
              var before = JSON.stringify(m);
              m.form = form; m.gloss = gloss; m.etymology = et; m.notes = notes; m.tags = tagsFrom(tagLabels, m.tags);
              m.letter = L.letter; m.section = 'sec-' + L.key;
              if (rootRefs.length) m.root_refs = rootRefs; else delete m.root_refs;
              if (JSON.stringify(m) === before) fail('No hay cambios que guardar.');
              return { files: files, message: 'Morfema: editar ' + form, after: reload };
            });
          });
        }
      });
    });
  }

  /* ---------- Integración en cada página ---------- */
  function guard(p) { return function () { Promise.resolve().then(p).catch(function (e) { console.error(e); alert('No se pudo abrir el editor: ' + e.message); }); }; }
  function bar(buttons) {
    return el('div', { class: 'ce-bar' }, [el('span', { class: 'ce-bar-label', text: 'Edición' })].concat(buttons));
  }
  function btn(text, onclick, cls) { return el('button', { type: 'button', class: 'ce-btn ' + (cls || ''), text: text, onclick: onclick }); }
  function observe(target, fn) { if (!target) return; fn(); new MutationObserver(fn).observe(target, { childList: true, subtree: true }); }
  var page = (location.pathname.split('/').pop() || 'index.html').replace(/\.html$/, '') || 'index';

  function wireNav() {
    var nav = document.querySelector('.site-nav'); if (!nav || nav.querySelector('.ce-toggle')) return;
    var b = el('button', { type: 'button', class: 'ce-toggle' + (editOn() ? ' on' : ''), title: editOn() ? 'Modo edición activo' : 'Activar el modo edición', text: editOn() ? '✎ Editando' : '✎ Editar', onclick: tokenDialog });
    nav.appendChild(b);
  }

  function wirePage() {
    if (!editOn()) return;
    var main = document.querySelector('main.wrap');
    if (page === 'lexico') {
      var target = document.getElementById('lex-content');
      target.parentNode.insertBefore(bar([btn('+ Nueva raíz', guard(function () { return rootDialog(null); }), 'primary'), btn('+ Nuevo vocablo', guard(function () { return wordDialog(null, null); })), btn('+ Nuevo morfema', guard(function () { return morphDialog(null); }))]), document.querySelector('nav.alphabet'));
    } else if (page === 'raiz') {
      var rootId = new URLSearchParams(location.search).get('id'), box = document.getElementById('root-content');
      observe(box, function () {
        var sheet = box.querySelector('.root-sheet'); if (!sheet || sheet.dataset.ce) return; sheet.dataset.ce = '1';
        var head = sheet.querySelector('.root-head');
        head.parentNode.insertBefore(el('div', { style: 'margin-top:18px' }, [bar([
          btn('✎ Editar raíz', guard(function () { return rootDialog(rootId); }), 'primary'),
          btn('+ Añadir vocablo', guard(function () { return wordDialog(rootId, null); })),
          btn('+ Nuevo morfema', guard(function () { return morphDialog(null); }))])]), head.nextSibling);
        sheet.querySelectorAll('.word-card').forEach(function (card) {
          var a = card.querySelector('.word-form a[href^="vocablos.html#"]'); if (!a) return;
          var wid = decodeURIComponent(a.getAttribute('href').split('#')[1]);
          var ext = card.querySelector('a[href^="raiz.html?id="]');
          var rid = ext ? new URLSearchParams(ext.getAttribute('href').split('?')[1]).get('id') : rootId;
          card.appendChild(el('div', { class: 'ce-card-actions' }, [el('button', { type: 'button', class: 'ce-btn small', text: '✎ Editar', onclick: guard(function () { return wordDialog(rid, wid); }) })]));
        });
      });
    } else if (page === 'vocablos') {
      var wc = document.getElementById('word-content');
      wc.parentNode.insertBefore(bar([btn('+ Nuevo vocablo', guard(function () { return wordDialog(null, null); }), 'primary'), btn('+ Nueva raíz', guard(function () { return rootDialog(null); }))]), document.getElementById('word-alphabet'));
      observe(wc, function () {
        wc.querySelectorAll('tr[id^="lexeme-"]:not([data-ce])').forEach(function (tr) {
          tr.dataset.ce = '1';
          var rl = tr.querySelector('a.root-link[data-root-id]'), td = tr.querySelector('td.word-form');
          if (rl && td) td.appendChild(el('button', { type: 'button', class: 'ce-btn small ce-inline', title: 'Editar vocablo', text: '✎', onclick: guard(function () { return wordDialog(rl.dataset.rootId, tr.id); }) }));
        });
      });
    } else if (page === 'morfemas') {
      var mb = document.getElementById('morph-body');
      var tr0 = document.querySelector('.tool-row');
      tr0.parentNode.insertBefore(bar([btn('+ Nuevo morfema', guard(function () { return morphDialog(null); }), 'primary')]), tr0);
      observe(mb, function () {
        mb.querySelectorAll('tr[id]:not([data-ce])').forEach(function (tr) {
          tr.dataset.ce = '1';
          var td = tr.querySelector('td.form');
          if (td) td.appendChild(el('button', { type: 'button', class: 'ce-btn small ce-inline', title: 'Editar morfema', text: '✎', onclick: guard(function () { return morphDialog(tr.id); }) }));
        });
      });
    } else if (page === 'semantica') {
      var tr1 = document.querySelector('.tool-row') || (main && main.firstElementChild);
      if (tr1) tr1.parentNode.insertBefore(bar([el('span', { class: 'ce-help', text: 'Los campos semánticos se asignan en cada vocablo (✎ Editar en la ficha de la raíz o en Vocablos).' }), btn('+ Nuevo vocablo', guard(function () { return wordDialog(null, null); }))]), tr1);
    }
  }

  function init() {
    document.head.appendChild(el('style', { text: CSS }));
    wireNav(); wirePage();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
