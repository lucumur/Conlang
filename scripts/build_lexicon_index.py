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

# Migración temporal: formalizar BO-, -UR y -TRO en la familia BAT.
bpath = LEX/'b.json'
mpath = LEX/'morphemes.json'
bdata = json.loads(bpath.read_text(encoding='utf-8'))
mdata = json.loads(mpath.read_text(encoding='utf-8'))
changed = False

morphs = mdata.get('morphemes', [])
byid = {m.get('id'): m for m in morphs}

def ensure_morph(mid, form, gloss, label, letter, section, notes=None):
    global changed
    if mid in byid:
        m = byid[mid]
        desired = {
            'form': form,
            'gloss': gloss,
            'tags': [{'class':'generic','label':label}],
            'letter': letter,
            'section': section,
            'etymology': None,
            'notes': notes or [],
            'row_class': ''
        }
        for k,v in desired.items():
            if m.get(k) != v:
                m[k] = v
                changed = True
        return m
    m = {
        'id': mid,
        'form': form,
        'gloss': gloss,
        'tags': [{'class':'generic','label':label}],
        'letter': letter,
        'section': section,
        'etymology': None,
        'notes': notes or [],
        'row_class': ''
    }
    morphs.append(m)
    byid[mid] = m
    changed = True
    return m

ensure_morph('morph-bo-mutual-action', '*BO-', 'algo hecho entre dos', 'prefijo', 'B', 'sec-b')
ensure_morph('morph-tro-mechanical', '*-TRO', 'objeto mecánico', 'sufijo', 'T', 'sec-t')

mur = byid.get('morph-ur-3')
if mur is None:
    raise SystemExit('morph-ur-3 not found')
new_ur_gloss = 'adjetivo; también superlativizador'
new_ur_notes = [
    'Canónico: -UR forma adjetivos.',
    'También puede emplearse con valor superlativo; se mantiene la ambigüedad formal.'
]
if mur.get('gloss') != new_ur_gloss:
    mur['gloss'] = new_ur_gloss
    changed = True
if mur.get('notes') != new_ur_notes:
    mur['notes'] = new_ur_notes
    changed = True

root = next((e for e in bdata.get('entries',[]) if e.get('id') == 'root-bat'), None)
if root is None:
    raise SystemExit('root-bat not found')
words_by_id = {w.get('id'): w for w in root.get('words',[])}

def set_word(wid, analysis_html, analysis_text, refs):
    global changed
    w = words_by_id.get(wid)
    if w is None:
        raise SystemExit(f'{wid} not found')
    desired = {'analysis_html': analysis_html, 'analysis_text': analysis_text, 'refs': refs}
    for k,v in desired.items():
        if w.get(k) != v:
            w[k] = v
            changed = True

set_word(
    'lexeme-bobatlas',
    '<a class="morph-link" href="#morph-bo-mutual-action">BO-</a> + BAT + L (extensión lexicalizada) + <a class="morph-link" href="#morph-as">-AS</a>',
    'BO- + BAT + L (extensión lexicalizada) + -AS',
    [{'id':'morph-bo-mutual-action','label':'BO-'},{'id':'morph-as','label':'-AS'}]
)
set_word(
    'lexeme-bobatla',
    '<a class="morph-link" href="#morph-bo-mutual-action">BO-</a> + BAT + L (extensión lexicalizada) + <a class="morph-link" href="#morph-a-2">-A</a>',
    'BO- + BAT + L (extensión lexicalizada) + -A',
    [{'id':'morph-bo-mutual-action','label':'BO-'},{'id':'morph-a-2','label':'-A'}]
)
set_word(
    'lexeme-batlur',
    'BAT + L (extensión lexicalizada) + <a class="morph-link" href="#morph-ur-3">-UR</a>',
    'BAT + L (extensión lexicalizada) + -UR',
    [{'id':'morph-ur-3','label':'-UR'}]
)
set_word(
    'lexeme-batitro',
    'BAT + <a class="morph-link" href="#morph-it-frequentative">-IT-</a> + <a class="morph-link" href="#morph-tro-mechanical">-TRO</a>',
    'BAT + -IT- + -TRO',
    [{'id':'morph-it-frequentative','label':'-IT-'},{'id':'morph-tro-mechanical','label':'-TRO'}]
)

if changed:
    bpath.write_text(json.dumps(bdata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    mpath.write_text(json.dumps(mdata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

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

if changed:
    subprocess.run(['git','config','user.name','ChatGPT'], check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'], check=True)
    subprocess.run(['git','add','lexico/b.json','lexico/morphemes.json','lexico/index.json'], check=True)
    subprocess.run(['git','commit','-m','Canonizar BO UR TRO en BAT'], check=True)
    subprocess.run(['git','push'], check=True)
