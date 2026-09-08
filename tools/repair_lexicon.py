from pathlib import Path
import base64
import gzip
import html
import re
import subprocess

p = Path('lexico.html')
src = p.read_text(encoding='utf-8')
m = re.search(r'<script id="lex-gzip"[^>]*>(.*?)</script>', src, re.S)

data = None
if m:
    try:
        data = gzip.decompress(base64.b64decode(m.group(1).strip())).decode('utf-8')
    except Exception:
        data = None

# El bloque gzip actual quedó truncado. Recuperar las cuatro partes históricas
# directamente desde los blobs que existían antes de eliminarlas del repo.
if data is None:
    blob_shas = [
        '971147a09147acd9b722e1693390ec736094f5ca',
        'b9a1005c588445a8a9037b3455fbc1323d9114b3',
        'b5acc3102330da3926a6015b0b88770ab511ae3b',
        '34f51ca51cc17b31702d0889afc4964df3a217a3',
    ]
    parts = []
    for sha in blob_shas:
        parts.append(subprocess.check_output(['git','cat-file','-p',sha]).decode('utf-8'))
    data = '\n'.join(parts)

data = data.replace('#Nativo', '#Nat-plen').replace('#Mod', '#Nat-mod')
data = data.replace('Š', 'Ŝ').replace('š', 'ŝ')
data = data.replace('[S / Ŝ]', '[S]')

fixed = []
inserted = False
for line in data.splitlines():
    if not inserted and line.lstrip().startswith('*Ŝ'):
        fixed.extend(['', '[Ŝ]', ''])
        inserted = True
    fixed.append(line)
data = '\n'.join(fixed)

origins = {
    'Nat-plen','Nat-mod','Nova','Latin','Frances','Español','Portugues',
    'Italico','Germanico','Anglo','Griego','Slavo','Celta','Arabe','Baltico',
    'Persa','Sinico','Indico'
}

sections = []
current = None
last = None
for raw in data.splitlines():
    t = raw.strip()
    if not t:
        continue
    sec = re.fullmatch(r'\[([^\]]+)\]', t)
    if sec:
        current = {'name': sec.group(1), 'entries': []}
        sections.append(current)
        last = None
        continue
    if t.startswith('Nota visible:') or t.startswith('Nota:'):
        if last is not None:
            last['note'] = re.sub(r'^Nota(?: visible)?:\s*', '', t)
        continue
    if current is None or '|' not in raw:
        continue
    left, right = raw.split('|', 1)
    left, right = left.strip(), right.strip()
    if '=' in left:
        form, gloss = map(str.strip, left.split('=', 1))
    else:
        form, gloss = left, ''
    toks = right.split()
    last = {
        'form': form,
        'gloss': gloss,
        'tags': [x[1:] for x in toks if x.startswith('#')],
        'extras': [x for x in toks if not x.startswith('#')],
        'note': ''
    }
    current['entries'].append(last)

def css_tag(tag):
    return (tag.lower().replace('ñ','n').replace('á','a').replace('é','e')
            .replace('í','i').replace('ó','o').replace('ú','u'))

nav = []
body = []
for i, sec in enumerate(sections, 1):
    sid = f'sec-{i}'
    nav.append(f'<a href="#{sid}">{html.escape(sec["name"])}</a>')
    rows = []
    for e in sec['entries']:
        tags = []
        for tag in e['tags']:
            cls = css_tag(tag) if tag in origins else 'generic'
            tags.append(f'<span class="tag {html.escape(cls)}">{html.escape(tag)}</span>')
        for extra in e['extras']:
            tags.append(f'<span class="meta-extra">{html.escape(extra)}</span>')
        note = f'<div class="entry-note">{html.escape(e["note"])}</div>' if e['note'] else ''
        rows.append(
            '<tr>'
            f'<td class="form"><code>{html.escape(e["form"])}</code></td>'
            f'<td class="gloss">{html.escape(e["gloss"])}{note}</td>'
            f'<td class="tags">{"".join(tags)}</td>'
            '</tr>'
        )
    body.append(
        f'<section class="lex-section" id="{sid}">\n'
        f'  <h2>{html.escape(sec["name"])}</h2>\n'
        '  <div class="table-wrap">\n'
        '    <table class="lex-table">\n'
        '      <thead><tr><th>Forma</th><th>Glosa</th><th>Etiquetas</th></tr></thead>\n'
        f'      <tbody>{"".join(rows)}</tbody>\n'
        '    </table>\n'
        '  </div>\n'
        '</section>'
    )

output = f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Léxico · Conlang</title>
  <meta name="description" content="Léxico canónico del conlang">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
<header class="page-header">
  <div class="wrap">
    <div class="brand"><a href="index.html">CONLANG</a></div>
    <nav class="site-nav" aria-label="Navegación principal">
      <a href="index.html">Inicio</a>
      <a href="lexico.html">Léxico</a>
      <a href="pronombres.html">Pronombres</a>
      <a href="gramatica.html">Gramática</a>
      <a href="fonologia.html">Fonología</a>
      <a href="historia.html">Historia</a>
    </nav>
  </div>
</header>
<main class="wrap">
  <section class="hero compact">
    <p class="eyebrow">Fuente léxica</p>
    <h1>Léxico</h1>
    <p>Inventario de raíces, afijos, glosas y etiquetas actualmente documentadas. Todo el léxico está escrito directamente en este archivo HTML.</p>
  </section>
  <nav class="alphabet" aria-label="Índice alfabético">{''.join(nav)}</nav>
  {''.join(body)}
</main>
<footer class="page-footer"><div class="wrap">Fuente canónica de trabajo del proyecto.</div></footer>
</body>
</html>
'''

assert 'DecompressionStream' not in output
assert 'No se pudo cargar el léxico' not in output
assert '>S<' in output and '>Ŝ<' in output
assert 'Š' not in output
assert '#Foranea' not in output
p.write_text(output, encoding='utf-8')
print(f'Escritas {sum(len(s["entries"]) for s in sections)} entradas en {len(sections)} secciones.')
