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

def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def entry_by_id(data, eid):
    return next(e for e in data.get('entries', []) if e.get('id') == eid)

def word_by_id(entry, wid):
    return next(w for w in entry.get('words', []) if w.get('id') == wid)

migration_changed = False

# --- Migración canónica solicitada: SE-, LOM-, BARD y BAS ---
b_path = LEX / 'b.json'
b = load_json(b_path)

barb = entry_by_id(b, 'root-barb')
lombarbin = word_by_id(barb, 'lexeme-lombarbin')
lombarbin.update({
    'analysis_html': '<a class="morph-link" href="#morph-lom-long">LOM-</a> + BARB + <a class="morph-link" href="#morph-in">-IN</a>',
    'analysis_text': 'LOM- + BARB + -IN',
    'refs': [
        {'id': 'morph-lom-long', 'label': 'LOM-'},
        {'id': 'morph-in', 'label': '-IN'}
    ]
})
sebarbin = word_by_id(barb, 'lexeme-sebarbin')
sebarbin.update({
    'analysis_html': '<a class="morph-link" href="#morph-se-privative">SE-</a> + BARB + <a class="morph-link" href="#morph-in">-IN</a>',
    'analysis_text': 'SE- + BARB + -IN',
    'refs': [
        {'id': 'morph-se-privative', 'label': 'SE-'},
        {'id': 'morph-in', 'label': '-IN'}
    ]
})

bard = entry_by_id(b, 'root-bard')
for w in bard.get('words', []):
    if w.get('id') == 'lexeme-barda' or w.get('form') == 'barda':
        w.update({
            'id': 'lexeme-bardo',
            'form': 'bardo',
            'gloss': 'borde, orilla',
            'analysis_html': 'BARD + <a class="morph-link" href="#morph-o">-O</a>',
            'analysis_text': 'BARD + -O',
            'refs': [{'id': 'morph-o', 'label': '-O'}],
            'tags': [{'class': 'generic', 'label': 'Inanimado O'}]
        })
    if w.get('id') == 'lexeme-robarda' or w.get('form') == 'robarda':
        w.update({
            'id': 'lexeme-robardo',
            'form': 'robardo',
            'gloss': 'marco, recuadro',
            'analysis_html': '<a class="morph-link" href="#morph-ro-2">RO-</a> + BARD + <a class="morph-link" href="#morph-o">-O</a>',
            'analysis_text': 'RO- + BARD + -O',
            'refs': [
                {'id': 'morph-ro-2', 'label': 'RO-'},
                {'id': 'morph-o', 'label': '-O'}
            ],
            'tags': [{'class': 'generic', 'label': 'Inanimado O'}]
        })

bas = entry_by_id(b, 'root-bas')
bas['gloss'] = 'base'
bas['words'] = [
    {
        'id': 'lexeme-basas', 'form': 'basas', 'gloss': 'fundar, establecer',
        'analysis_html': 'BAS + <a class="morph-link" href="#morph-as">-AS</a>',
        'analysis_text': 'BAS + -AS',
        'refs': [{'id': 'morph-as', 'label': '-AS'}],
        'tags': [{'class': 'generic', 'label': 'Predicado AS'}],
        'semantic_fields': ['procesos', 'relaciones']
    },
    {
        'id': 'lexeme-basis', 'form': 'basis', 'gloss': 'basarse en...',
        'analysis_html': 'BAS + <a class="morph-link" href="#morph-is">-IS</a>',
        'analysis_text': 'BAS + -IS',
        'refs': [{'id': 'morph-is', 'label': '-IS'}],
        'tags': [{'class': 'generic', 'label': 'Predicado IS'}],
        'semantic_fields': ['relaciones', 'procesos']
    },
    {
        'id': 'lexeme-basida', 'form': 'basida', 'gloss': 'elemento',
        'analysis_html': 'BAS + <a class="morph-link" href="#morph-id">-ID-</a> + <a class="morph-link" href="#morph-a-2">-A</a>',
        'analysis_text': 'BAS + -ID- + -A',
        'refs': [{'id': 'morph-id', 'label': '-ID-'}, {'id': 'morph-a-2', 'label': '-A'}],
        'tags': [{'class': 'generic', 'label': 'Nomen A'}],
        'semantic_fields': ['objetos', 'relaciones']
    },
    {
        'id': 'lexeme-basidel', 'form': 'basidel', 'gloss': 'elemental, básico',
        'analysis_html': 'BAS + <a class="morph-link" href="#morph-id">-ID-</a> + <a class="morph-link" href="#morph-el">-EL</a>',
        'analysis_text': 'BAS + -ID- + -EL',
        'refs': [{'id': 'morph-id', 'label': '-ID-'}, {'id': 'morph-el', 'label': '-EL'}],
        'tags': [{'class': 'generic', 'label': 'Adjetivo'}],
        'semantic_fields': ['cualidades', 'relaciones']
    },
    {
        'id': 'lexeme-basaj', 'form': 'basaj', 'gloss': 'cimientos, principios',
        'analysis_html': 'BAS + <a class="morph-link" href="#morph-aj">-AJ</a>',
        'analysis_text': 'BAS + -AJ',
        'refs': [{'id': 'morph-aj', 'label': '-AJ'}],
        'tags': [{'class': 'generic', 'label': 'Plural nominal'}],
        'semantic_fields': ['relaciones', 'forma']
    },
    {
        'id': 'lexeme-sobasal', 'form': 'sobasal', 'gloss': 'sótano',
        'analysis_html': '<a class="morph-link" href="#morph-so-sub">SO-</a> + BAS + <a class="morph-link" href="#morph-al-3">-AL</a>',
        'analysis_text': 'SO- + BAS + -AL',
        'refs': [{'id': 'morph-so-sub', 'label': 'SO-'}, {'id': 'morph-al-3', 'label': '-AL'}],
        'tags': [{'class': 'generic', 'label': 'Locativo AL'}],
        'semantic_fields': ['lugares', 'objetos']
    },
    {
        'id': 'lexeme-basedral', 'form': 'basedral', 'gloss': 'cuarteles',
        'analysis_html': 'BAS + <a class="morph-link" href="#morph-edral">-EDRAL</a>',
        'analysis_text': 'BAS + -EDRAL',
        'refs': [{'id': 'morph-edral', 'label': '-EDRAL'}],
        'tags': [{'class': 'generic', 'label': 'Edificio'}],
        'semantic_fields': ['lugares', 'relaciones']
    },
    {
        'id': 'lexeme-plabasal', 'form': 'plabasal', 'gloss': 'plataforma, base',
        'analysis_html': '<a class="morph-link" href="#morph-pla">PLA-</a> + BAS + <a class="morph-link" href="#morph-al-3">-AL</a>',
        'analysis_text': 'PLA- + BAS + -AL',
        'refs': [{'id': 'morph-pla', 'label': 'PLA-'}, {'id': 'morph-al-3', 'label': '-AL'}],
        'tags': [{'class': 'generic', 'label': 'Locativo AL'}],
        'semantic_fields': ['objetos', 'lugares', 'forma']
    }
]
save_json(b_path, b)
migration_changed = True

l_path = LEX / 'l.json'
l = load_json(l_path)
long_root = entry_by_id(l, 'root-long')
long_root['form'] = '*LON-G'
long_root['gloss'] = 'largo, alargado, elongado'
save_json(l_path, l)

m_path = LEX / 'morphemes.json'
mdata = load_json(m_path)
morphs = mdata.setdefault('morphemes', [])
by_id = {m.get('id'): m for m in morphs}

def upsert_morph(mid, form, gloss, letter, tag):
    obj = {
        'id': mid,
        'form': form,
        'gloss': gloss,
        'tags': [{'class': 'generic', 'label': tag}],
        'letter': letter,
        'section': 'sec-' + letter.lower(),
        'row_class': ''
    }
    if mid in by_id:
        by_id[mid].update(obj)
    else:
        morphs.append(obj)
        by_id[mid] = obj

upsert_morph('morph-se-privative', '*SE-', 'privativo; sin', 'S', 'Privativo')
upsert_morph('morph-lom-long', '*LOM-', 'largo, alargado, elongado; procede de *LON-G', 'L', 'Derivativo')
upsert_morph('morph-edral', '*-EDRAL', 'edificio; extensión de *-ED-', 'E', 'Derivativo')
upsert_morph('morph-pla', '*PLA-', 'morfema derivativo; valor semántico general por definir', 'P', 'Derivativo')
if 'morph-so-sub' in by_id:
    by_id['morph-so-sub']['gloss'] = 'bajo, debajo; por extensión atenuativo, en grado menor'
save_json(m_path, mdata)

# --- Generación normal del índice ---
roots=[]
words=[]
for letter,key in LETTER_FILES:
    data=load_json(LEX/f'{key}.json')
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

mdata=load_json(LEX/'morphemes.json')
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

# Persistir la migración desde el workflow que ya tiene contents:write.
if migration_changed:
    subprocess.run(['git','config','user.name','ChatGPT'], check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'], check=True)
    subprocess.run(['git','add','lexico/b.json','lexico/l.json','lexico/morphemes.json','lexico/index.json'], check=True)
    staged = subprocess.run(['git','diff','--cached','--quiet'])
    if staged.returncode != 0:
        subprocess.run(['git','commit','-m','Canonizar SE LOM BARD y BAS'], check=True)
        subprocess.run(['git','push'], check=True)
