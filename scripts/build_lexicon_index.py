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

def save_pretty(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

changed = False

# Eliminar el duplicado accidental de la raíz *AJN- «cualquiera».
ap = LEX / 'a.json'
adata = json.loads(ap.read_text(encoding='utf-8'))
old_len = len(adata.get('entries', []))
adata['entries'] = [e for e in adata.get('entries', []) if e.get('id') != 'root-ajn-2']
if len(adata['entries']) != old_len:
    save_pretty(ap, adata)
    changed = True

# AJN/EJN familiares son sufijos personales, no raíces duplicadas.
mp = LEX / 'morphemes.json'
mdata = json.loads(mp.read_text(encoding='utf-8'))
m_changed = False
for m in mdata.get('morphemes', []):
    if m.get('id') == 'morph-ajn-family':
        gloss = 'sufijo de persona (coallegados)'
        notes = ['Sufijo personal para coallegados. Atestiguado en avajn y en otras formas familiares como pajn y frajn.']
        if m.get('gloss') != gloss or m.get('notes') != notes:
            m['gloss'] = gloss
            m['notes'] = notes
            m_changed = True
    elif m.get('id') == 'morph-ejn-family':
        gloss = 'variante femenina de -AJN'
        notes = ['Variante femenina del sufijo personal -AJN.']
        if m.get('gloss') != gloss or m.get('notes') != notes:
            m['gloss'] = gloss
            m['notes'] = notes
            m_changed = True
if m_changed:
    save_pretty(mp, mdata)
    changed = True

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

if changed and os.environ.get('GITHUB_ACTIONS') == 'true':
    subprocess.run(['git','config','user.name','ChatGPT'], check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'], check=True)
    subprocess.run(['git','add','lexico/a.json','lexico/morphemes.json','lexico/index.json'], check=True)
    subprocess.run(['git','commit','-m','Corregir duplicado AJN y sufijos familiares'], check=True)
    subprocess.run(['git','push'], check=True)
