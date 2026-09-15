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

# Migración canónica: el antiguo prefijo recíproco MU- fue sustituido por O-.
# Es idempotente y sólo afecta a las cinco formas que estaban enlazadas al
# antiguo morfema; *-MU gerundivo y otras secuencias mu permanecen intactas.
def migrate_mutual_prefix():
    path = LEX / 'a.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    replacements = {
        'lexeme-muarzos': ('lexeme-oarzos', 'oarẑos'),
        'lexeme-muarza': ('lexeme-oarza', 'oarẑa'),
        'lexeme-muastropos': ('lexeme-oastropos', 'oastropos'),
        'lexeme-muastropa': ('lexeme-oastropa', 'oastropa'),
        'lexeme-muathlos': ('lexeme-oathlos', 'oaθlos'),
    }
    changed = False
    for entry in data.get('entries', []):
        for word in entry.get('words', []):
            old_id = word.get('id')
            if old_id not in replacements:
                continue
            new_id, new_form = replacements[old_id]
            word['id'] = new_id
            word['form'] = new_form
            word['analysis_html'] = word.get('analysis_html', '').replace('#morph-mu-2', '#morph-o-mutual').replace('>MU-</a>', '>O-</a>')
            word['analysis_text'] = word.get('analysis_text', '').replace('MU- +', 'O- +')
            for ref in word.get('refs', []):
                if ref.get('id') == 'morph-mu-2':
                    ref['id'] = 'morph-o-mutual'
                    ref['label'] = 'O-'
            changed = True
    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        subprocess.run(['git', 'add', 'lexico/a.json'], cwd=ROOT, check=True)

migrate_mutual_prefix()

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
