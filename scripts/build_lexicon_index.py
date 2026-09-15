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

# Incorporación canónica de las dos familias homónimas *BAL- ya reservadas.
# Es idempotente: sólo completa las entradas mientras sigan sin repertorio.
def canonize_bal_families():
    path = LEX / 'b.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    changed = False
    for entry in data.get('entries', []):
        if entry.get('id') == 'root-bal' and not entry.get('words'):
            entry['row_class'] = 'lex-root-row'
            entry['words'] = [
                {
                    'id': 'lexeme-balos', 'form': 'balos', 'gloss': 'bailar (lento)',
                    'analysis_html': 'BAL + <a class="morph-link" href="#morph-os">-OS</a>',
                    'analysis_text': 'BAL + -OS',
                    'refs': [{'id': 'morph-os', 'label': '-OS'}],
                    'tags': [{'class': 'generic', 'label': 'Predicado OS'}],
                    'semantic_fields': ['danza', 'movimiento', 'baile']
                },
                {
                    'id': 'lexeme-balonton', 'form': 'balonton', 'gloss': 'bailarín',
                    'analysis_html': 'BAL + ONTON (formante léxico; función aún no formalizada)',
                    'analysis_text': 'BAL + ONTON (formante léxico; función aún no formalizada)',
                    'refs': [],
                    'tags': [{'class': 'generic', 'label': 'Humano'}],
                    'semantic_fields': ['danza', 'personas', 'baile']
                },
                {
                    'id': 'lexeme-parbalon', 'form': 'parbalon', 'gloss': 'pareja de baile',
                    'analysis_html': '<a class="morph-link" href="#root-par">PAR</a> + BAL + <a class="morph-link" href="#morph-on">-ON</a>',
                    'analysis_text': 'PAR + BAL + -ON',
                    'refs': [{'id': 'root-par', 'label': 'PAR'}, {'id': 'morph-on', 'label': '-ON'}],
                    'tags': [{'class': 'generic', 'label': 'Humano ON'}],
                    'semantic_fields': ['danza', 'parejas', 'personas']
                },
                {
                    'id': 'lexeme-bala', 'form': 'bala', 'gloss': 'baile',
                    'analysis_html': 'BAL + <a class="morph-link" href="#morph-a-2">-A</a>',
                    'analysis_text': 'BAL + -A',
                    'refs': [{'id': 'morph-a-2', 'label': '-A'}],
                    'tags': [{'class': 'generic', 'label': 'Nomen A'}],
                    'semantic_fields': ['danza', 'baile', 'artes escénicas']
                },
                {
                    'id': 'lexeme-balezha', 'form': 'baleẑa', 'gloss': 'danza (disciplina)',
                    'analysis_html': 'BAL + <a class="morph-link" href="#morph-eza">-EẐA</a>',
                    'analysis_text': 'BAL + -EẐA',
                    'refs': [{'id': 'morph-eza', 'label': '-EẐA'}],
                    'tags': [{'class': 'generic', 'label': 'Nomen abstracto'}],
                    'semantic_fields': ['danza', 'disciplinas', 'artes escénicas']
                }
            ]
            changed = True
        elif entry.get('id') == 'root-bal-2' and not entry.get('words'):
            entry['row_class'] = 'lex-root-row'
            entry['words'] = [
                {
                    'id': 'lexeme-dorbalo', 'form': 'dorbalo', 'gloss': 'giba, joroba',
                    'analysis_html': 'DOR (segmento no formalizado) + BAL + <a class="morph-link" href="#morph-o">-O</a>',
                    'analysis_text': 'DOR (segmento no formalizado) + BAL + -O',
                    'refs': [{'id': 'morph-o', 'label': '-O'}],
                    'tags': [{'class': 'generic', 'label': 'Nomen O'}],
                    'semantic_fields': ['anatomía', 'espalda', 'formas corporales']
                },
                {
                    'id': 'lexeme-dorbalin', 'form': 'dorbalin', 'gloss': 'jorobado',
                    'analysis_html': 'DOR (segmento no formalizado) + BAL + <a class="morph-link" href="#morph-in">-IN</a>',
                    'analysis_text': 'DOR (segmento no formalizado) + BAL + -IN',
                    'refs': [{'id': 'morph-in', 'label': '-IN'}],
                    'tags': [{'class': 'generic', 'label': 'Participio animante'}],
                    'semantic_fields': ['anatomía', 'personas', 'formas corporales']
                },
                {
                    'id': 'lexeme-virbalo', 'form': 'virbalo', 'gloss': 'glande',
                    'analysis_html': '<a class="morph-link" href="#root-vir">VIR</a> + BAL + <a class="morph-link" href="#morph-o">-O</a>',
                    'analysis_text': 'VIR + BAL + -O',
                    'refs': [{'id': 'root-vir', 'label': 'VIR'}, {'id': 'morph-o', 'label': '-O'}],
                    'tags': [{'class': 'generic', 'label': 'Nomen O'}],
                    'semantic_fields': ['anatomía', 'genitales', 'masculino']
                },
                {
                    'id': 'lexeme-virbalcha', 'form': 'virbalĉa', 'gloss': 'balanitis',
                    'analysis_html': '<a class="morph-link" href="#root-vir">VIR</a> + BAL + Ĉ (formante léxico no formalizado) + <a class="morph-link" href="#morph-a-2">-A</a>',
                    'analysis_text': 'VIR + BAL + Ĉ (formante léxico no formalizado) + -A',
                    'refs': [{'id': 'root-vir', 'label': 'VIR'}, {'id': 'morph-a-2', 'label': '-A'}],
                    'tags': [{'class': 'generic', 'label': 'Nomen A'}],
                    'semantic_fields': ['salud', 'genitales', 'inflamación']
                },
                {
                    'id': 'lexeme-balono', 'form': 'balono', 'gloss': 'balón',
                    'analysis_html': 'BAL + ON (extensión lexicalizada; función no formalizada) + <a class="morph-link" href="#morph-o">-O</a>',
                    'analysis_text': 'BAL + ON (extensión lexicalizada; función no formalizada) + -O',
                    'refs': [{'id': 'morph-o', 'label': '-O'}],
                    'tags': [{'class': 'generic', 'label': 'Nomen O'}],
                    'semantic_fields': ['objetos', 'deportes', 'pelotas']
                },
                {
                    'id': 'lexeme-balzheten', 'form': 'balẑeten', 'gloss': 'ballena',
                    'analysis_html': 'BAL + <a class="morph-link" href="#root-zet-2">ẐET</a> + <a class="morph-link" href="#morph-en">-EN</a>',
                    'analysis_text': 'BAL + ẐET + -EN',
                    'refs': [{'id': 'root-zet-2', 'label': 'ẐET'}, {'id': 'morph-en', 'label': '-EN'}],
                    'tags': [{'class': 'generic', 'label': 'Animado EN'}],
                    'semantic_fields': ['fauna', 'cetáceos', 'mamíferos marinos']
                },
                {
                    'id': 'lexeme-balonas', 'form': 'balonas', 'gloss': 'lanzar pelota',
                    'analysis_html': 'BAL + <a class="morph-link" href="#morph-onas">-ONAS</a>',
                    'analysis_text': 'BAL + -ONAS',
                    'refs': [{'id': 'morph-onas', 'label': '-ONAS'}],
                    'tags': [{'class': 'generic', 'label': 'Predicado ONAS'}],
                    'semantic_fields': ['deportes', 'pelotas', 'lanzamiento']
                }
            ]
            changed = True
    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        subprocess.run(['git', 'add', 'lexico/b.json'], cwd=ROOT, check=True)

canonize_bal_families()

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
