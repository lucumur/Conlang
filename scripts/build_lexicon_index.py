from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LEX = ROOT / 'lexico'
MAP = ROOT / 'scripts' / 'semantic_backfill.json'

LETTER_FILES = [
    ('A','a'),('B','b'),('C','c'),('Ĉ','circ-c'),('D','d'),('E','e'),('F','f'),('G','g'),('Ĝ','circ-g'),
    ('I','i'),('J','j'),('K','k'),('L','l'),('M','m'),('N','n'),('O','o'),('P','p'),('R','r'),('S','s'),
    ('Ŝ','circ-s'),('T','t'),('Θ','theta'),('U','u'),('V','v'),('Z','z'),('Ẑ','circ-z')
]

def labels(tags):
    return [t.get('label','') for t in tags or []]

assignments=json.loads(MAP.read_text(encoding='utf-8'))
existing_vocab=set()
for _,key in LETTER_FILES:
    data=json.loads((LEX/f'{key}.json').read_text(encoding='utf-8'))
    for e in data.get('entries',[]):
        for w in e.get('words',[]):
            existing_vocab.update(w.get('semantic_fields',[]) or [])

proposed={field for fields in assignments.values() for field in fields}
unknown=sorted(proposed-existing_vocab)
if unknown:
    raise RuntimeError(f'Campos semánticos nuevos no autorizados: {unknown}')

matched=set()
applied=0
changed_paths=[]
for _,key in LETTER_FILES:
    path=LEX/f'{key}.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    changed=False
    for e in data.get('entries',[]):
        for w in e.get('words',[]):
            wid=w.get('id')
            if wid in assignments:
                matched.add(wid)
                if not (w.get('semantic_fields',[]) or []):
                    w['semantic_fields']=assignments[wid]
                    applied += 1
                    changed=True
    if changed:
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        changed_paths.append(str(path.relative_to(ROOT)))

unmatched=sorted(set(assignments)-matched)
if unmatched:
    raise RuntimeError(f'IDs no encontrados: {unmatched}')

roots=[]
words=[]
remaining=[]
for letter,key in LETTER_FILES:
    data=json.loads((LEX/f'{key}.json').read_text(encoding='utf-8'))
    for e in data.get('entries',[]):
        if e.get('kind')=='other':
            continue
        parts=[e.get('form',''),e.get('gloss',''),e.get('etymology') or '']+labels(e.get('tags'))
        for w in e.get('words',[]):
            semantic_fields=w.get('semantic_fields',[]) or []
            if len(semantic_fields) not in (2,3):
                remaining.append({'id':w.get('id'),'form':w.get('form'),'count':len(semantic_fields)})
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

if remaining:
    raise RuntimeError(f'Palabras fuera de la regla 2–3 campos: {remaining}')

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

commit_paths=changed_paths+['lexico/index.json']
if changed_paths:
    subprocess.run(['git','config','user.name','ChatGPT'],check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],check=True)
    subprocess.run(['git','add',*commit_paths],check=True)
    subprocess.run(['git','commit','-m','Completar campos semánticos canónicos [skip ci]'],check=True)
    subprocess.run(['git','push'],check=True)

print('SEMANTIC_CANONICAL_PERSIST', json.dumps({'assignments':len(assignments),'applied':applied,'changed_paths':changed_paths,'remaining_invalid':len(remaining)},ensure_ascii=False))
print(payload['counts'])
