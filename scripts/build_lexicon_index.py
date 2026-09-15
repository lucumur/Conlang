from pathlib import Path
import json
import os
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LEX = ROOT / 'lexico'

LETTER_FILES = [
    ('A','a'),('B','b'),('C','c'),('Ĉ','circ-c'),('D','d'),('E','e'),('F','f'),('G','g'),('Ĝ','circ-g'),
    ('I','i'),('J','j'),('K','k'),('L','l'),('M','m'),('N','n'),('O','o'),('P','p'),('R','r'),('S','s'),
    ('Ŝ','circ-s'),('T','t'),('Θ','theta'),('U','u'),('V','v'),('Z','z'),('Ẑ','circ-z')
]

def labels(tags):
    return [t.get('label','') for t in tags or []]

def save_pretty(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

changed = False

# Las notas sobre derivados concretos no pertenecen a la tarjeta de raíz.
ap = LEX / 'a.json'
data = json.loads(ap.read_text(encoding='utf-8'))
a_changed = False
for e in data.get('entries', []):
    eid = e.get('id')

    if eid == 'root-arz':
        if e.get('notes'):
            e['notes'] = []
            a_changed = True
        for w in e.get('words', []):
            if w.get('id') == 'lexeme-arzur':
                notes = ['El segmento final -ur queda sin análisis morfémico; no se identifica aquí con el superlativo -UR.']
                if w.get('notes') != notes:
                    w['notes'] = notes
                    a_changed = True

    elif eid == 'root-asv':
        if e.get('notes'):
            e['notes'] = []
            a_changed = True

    elif eid == 'root-av-3':
        if e.get('notes'):
            e['notes'] = []
            a_changed = True
        for w in e.get('words', []):
            if w.get('id') == 'lexeme-af':
                notes = ['Partícula comitativa procedente de la forma suelta av; la plosiva se fricatiza al quedar en posición final: av > af.']
                if w.get('notes') != notes:
                    w['notes'] = notes
                    a_changed = True

if a_changed:
    save_pretty(ap, data)
    changed = True

# Mostrar notas propias de las subentradas léxicas.
htmlp = ROOT / 'lexico.html'
html = htmlp.read_text(encoding='utf-8')
new_html = html

css_old = '.derived-analysis{margin-top:7px;color:var(--muted);font-size:.8rem}.derived-tags'
css_new = '.derived-analysis{margin-top:7px;color:var(--muted);font-size:.8rem}.derived-note{margin-top:7px;color:var(--muted);font-size:.8rem;font-style:italic}.derived-tags'
if css_old in new_html:
    new_html = new_html.replace(css_old, css_new, 1)

new_word_func = '''  function wordHTML(w){
    const sem=w.semantic_fields?.length?`<div class="derived-semantics"><span class="semantic-label">Campos</span>${w.semantic_fields.map(x=>`<span class="semantic-field">${esc(x)}</span>`).join('')}</div>`:'';
    const notes=(w.notes||[]).map(n=>`<div class="derived-note">${esc(n)}</div>`).join('');
    return`<article class="derived-entry" id="${esc(w.id)}"><div class="derived-word"><code>${esc(w.form)}</code></div><div class="derived-gloss">${esc(w.gloss)}</div>${w.analysis_html?`<div class="derived-analysis">${w.analysis_html}</div>`:''}${notes}${sem}${w.tags?.length?`<div class="derived-tags">${tagHTML(w.tags)}</div>`:''}</article>`;
  }'''
new_html, n = re.subn(
    r'  function wordHTML\(w\)\{.*?\}\n  function entryRow',
    new_word_func + '\n  function entryRow',
    new_html,
    count=1,
    flags=re.S
)
if new_html != html:
    htmlp.write_text(new_html, encoding='utf-8')
    changed = True

roots=[]
words=[]
for letter,key in LETTER_FILES:
    letter_data=json.loads((LEX/f'{key}.json').read_text(encoding='utf-8'))
    for e in letter_data.get('entries',[]):
        if e.get('kind')=='other':
            continue
        parts=[e.get('form',''),e.get('gloss',''),e.get('etymology') or '']+labels(e.get('tags'))
        for w in e.get('words',[]):
            semantic_fields=w.get('semantic_fields',[]) or []
            notes=w.get('notes',[]) or []
            parts += [w.get('form',''),w.get('gloss',''),w.get('analysis_text','')]+labels(w.get('tags'))+semantic_fields+notes
            words.append({
                'id':w['id'],'root_id':e['id'],'letter':letter,'key':key,
                'form':w.get('form',''),'gloss':w.get('gloss',''),
                'refs':[r.get('id') for r in w.get('refs',[]) if r.get('id')],
                'semantic_fields':semantic_fields,'notes':notes,
                'search':' '.join([w.get('form',''),w.get('gloss',''),w.get('analysis_text','')]+labels(w.get('tags'))+semantic_fields+notes)
            })
        roots.append({
            'id':e['id'],'letter':letter,'key':key,'form':e.get('form',''),'gloss':e.get('gloss',''),
            'tags':labels(e.get('tags')),'etymology':e.get('etymology'),'search':' '.join(parts)
        })

mdata=json.loads((LEX/'morphemes.json').read_text(encoding='utf-8'))
morphemes=[]
for m in mdata.get('morphemes',[]):
    morphemes.append({
        'id':m['id'],'letter':m.get('letter',''),'form':m.get('form',''),'gloss':m.get('gloss',''),
        'tags':labels(m.get('tags')),
        'search':' '.join([m.get('form',''),m.get('gloss','')]+labels(m.get('tags')))
    })

payload={
    'schema_version':1,
    'letters':[{'section':'sec-'+key,'letter':letter,'key':key,'file':f'lexico/{key}.json'} for letter,key in LETTER_FILES],
    'roots':roots,'words':words,'morphemes':morphemes,
    'counts':{'roots':len(roots),'words':len(words),'morphemes':len(morphemes)}
}
(LEX/'index.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(payload['counts'])

if changed and os.environ.get('GITHUB_ACTIONS') == 'true':
    subprocess.run(['git','config','user.name','ChatGPT'], check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'], check=True)
    subprocess.run(['git','add','lexico/a.json','lexico/index.json','lexico.html'], check=True)
    subprocess.run(['git','commit','-m','Mover notas de raíz a subentradas léxicas'], check=True)
    subprocess.run(['git','push'], check=True)
