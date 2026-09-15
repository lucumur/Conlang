from pathlib import Path
import json
import os
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

# Migración documental puntual: las reglas generales de afijos viven en morphemes.json,
# no en las notas de las raíces que casualmente los ejemplifican.
migration_changed = False

def save_pretty(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

ap = LEX / 'a.json'
a = json.loads(ap.read_text(encoding='utf-8'))
for e in a.get('entries', []):
    if e.get('form') == '*AV-' and e.get('gloss') == 'abuelo':
        if e.get('notes'):
            e['notes'] = []
            migration_changed = True
    elif e.get('form') == '*AV-' and e.get('gloss') == 'tener':
        wanted = ['La partícula comitativa af procede históricamente de av, forma suelta de esta raíz: av > af.']
        if e.get('notes') != wanted:
            e['notes'] = wanted
            migration_changed = True
    elif e.get('form') == '*AŜV-':
        wanted = ['La grafía canónica de la raíz es AŜV; la antigua ASV queda obsoleta.']
        if e.get('notes') != wanted:
            e['notes'] = wanted
            migration_changed = True
if migration_changed:
    save_pretty(ap, a)

bp = LEX / 'b.json'
b = json.loads(bp.read_text(encoding='utf-8'))
b_changed = False
for e in b.get('entries', []):
    if e.get('form') == '*BAB-L' and e.get('notes'):
        e['notes'] = []
        b_changed = True
if b_changed:
    save_pretty(bp, b)
    migration_changed = True

mp = LEX / 'morphemes.json'
md = json.loads(mp.read_text(encoding='utf-8'))
byid = {m.get('id'): m for m in md.get('morphemes', [])}
updates = {
    'morph-ajn-family': ['Terminación familiar productiva. Atestiguada en avajn y en otras formas familiares como pajn y frajn.'],
    'morph-ejn-family': ['Variante femenina de -AJN. Atestiguada en avejn «abuela materna».'],
    'morph-ajnda-family': ['Forma abstracta de -AJN. Atestiguada en avajnda «abolengo, ancestria».'],
    'morph-us-habit': ['Sufijo habituativo. Atestiguado en avus- → avuser «habitual» y avusa «hábito».'],
    'morph-il-partitive': ['Tipo de partitivo. Distinto de *-IL «inanimado» y de *IL- «de objeto largo, delgado». Atestiguado en avila «característica» y bablila «plática, charla».'],
    'morph-ucirc': ['Sufijo canónico atestiguado en babluĉos «balbucear» y babluĉa «balbuceo»; su valor semántico general aún no está definido.']
}
for mid, notes in updates.items():
    m = byid.get(mid)
    if m is not None and m.get('notes') != notes:
        m['notes'] = notes
        migration_changed = True
if migration_changed:
    save_pretty(mp, md)

roots=[]
words=[]
for letter,key in LETTER_FILES:
    data=json.loads((LEX/f'{key}.json').read_text(encoding='utf-8'))
    for e in data.get('entries',[]):
        if e.get('kind')=='other':
            continue
        parts=[e.get('form',''),e.get('gloss',''),e.get('etymology') or '']+labels(e.get('tags'))
        for w in e.get('words',[]):
            semantic_fields=w.get('semantic_fields',[]) or []
            parts += [w.get('form',''),w.get('gloss',''),w.get('analysis_text','')]+labels(w.get('tags'))+semantic_fields
            words.append({
                'id':w['id'],'root_id':e['id'],'letter':letter,'key':key,
                'form':w.get('form',''),'gloss':w.get('gloss',''),
                'refs':[r.get('id') for r in w.get('refs',[]) if r.get('id')],
                'semantic_fields':semantic_fields,
                'search':' '.join([w.get('form',''),w.get('gloss',''),w.get('analysis_text','')]+labels(w.get('tags'))+semantic_fields)
            })
        roots.append({
            'id':e['id'],'letter':letter,'key':key,'form':e.get('form',''),'gloss':e.get('gloss',''),
            'tags':labels(e.get('tags')),'etymology':e.get('etymology'),
            'search':' '.join(parts)
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

if migration_changed and os.environ.get('GITHUB_ACTIONS') == 'true':
    subprocess.run(['git','config','user.name','ChatGPT'], check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'], check=True)
    subprocess.run(['git','add','lexico/a.json','lexico/b.json','lexico/morphemes.json','lexico/index.json'], check=True)
    subprocess.run(['git','commit','-m','Centralizar reglas morfológicas en morfemas'], check=True)
    subprocess.run(['git','push'], check=True)
