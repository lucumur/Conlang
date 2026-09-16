from pathlib import Path
import json
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

# Migración canónica puntual: registrar *JO- como sufijo independiente
# y enlazar el uso atestiguado en jobaldol.
mpath = LEX/'morphemes.json'
mdata = json.loads(mpath.read_text(encoding='utf-8'))
mid = 'morph-jo-bald'
existing = next((m for m in mdata.get('morphemes',[]) if m.get('id') == mid), None)
if existing is None:
    mdata.setdefault('morphemes', []).append({
        'id': mid,
        'form': '*JO-',
        'gloss': 'sufijo; valor semántico por definir',
        'tags': [{'class':'generic','label':'sufijo'}],
        'letter': 'J',
        'section': 'sec-j',
        'etymology': None,
        'notes': ['Atestiguado en jobaldol. Su valor semántico general aún no está definido; no se identifica con *JO- «ohh!» ni con *-JO «mujer (alternativo)».'],
        'row_class': ''
    })
else:
    existing['form'] = '*JO-'
    existing['gloss'] = 'sufijo; valor semántico por definir'
    existing['tags'] = [{'class':'generic','label':'sufijo'}]
    existing['letter'] = 'J'
    existing['section'] = 'sec-j'
    existing['notes'] = ['Atestiguado en jobaldol. Su valor semántico general aún no está definido; no se identifica con *JO- «ohh!» ni con *-JO «mujer (alternativo)».']
mpath.write_text(json.dumps(mdata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

bpath = LEX/'b.json'
bdata = json.loads(bpath.read_text(encoding='utf-8'))
word = None
for e in bdata.get('entries',[]):
    for w in e.get('words',[]):
        if w.get('id') == 'lexeme-jobaldol':
            word = w
            break
    if word:
        break
if word is None:
    raise RuntimeError('lexeme-jobaldol no encontrado')
word['analysis_html'] = '<a class="morph-link" href="#morph-jo-bald">JO-</a> + BALD + <a class="morph-link" href="#morph-ol-2">-OL</a>'
word['analysis_text'] = 'JO- + BALD + -OL'
word['refs'] = [
    {'id':'morph-jo-bald','label':'JO-'},
    {'id':'morph-ol-2','label':'-OL'}
]
bpath.write_text(json.dumps(bdata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

subprocess.run(['git','config','user.name','ChatGPT'], check=True)
subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'], check=True)
subprocess.run(['git','add','lexico/morphemes.json','lexico/b.json'], check=True)
if subprocess.run(['git','diff','--cached','--quiet']).returncode != 0:
    subprocess.run(['git','commit','-m','Registrar sufijo JO- [skip ci]'], check=True)
    subprocess.run(['git','push'], check=True)

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
