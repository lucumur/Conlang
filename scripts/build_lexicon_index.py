from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
LEX = ROOT / 'lexico'

LETTER_FILES = [
    ('A','a'),('B','b'),('C','c'),('Ĉ','circ-c'),('D','d'),('E','e'),('F','f'),('G','g'),('Ĝ','circ-g'),
    ('I','i'),('J','j'),('Ĵ','circ-j'),('K','k'),('L','l'),('M','m'),('N','n'),('O','o'),('P','p'),('R','r'),('S','s'),
    ('Ŝ','circ-s'),('T','t'),('Θ','theta'),('U','u'),('V','v'),('Z','z'),('Ẑ','circ-z')
]

def labels(tags):
    return [t.get('label','') for t in tags or []]

def index_paradigma(p):
    """Réplica de indexParadigma en editor.js. None si el campo no es una tabla válida."""
    if not isinstance(p, dict):
        return None
    tipo = p.get('tipo')
    filas = p.get('filas')
    if tipo not in ('conjugacion', 'declinacion') or not isinstance(filas, list) or not filas:
        return None
    clean = []
    width = None
    for row in filas:
        if not isinstance(row, list) or not row:
            return None
        cells = []
        for c in row:
            if not isinstance(c, str):
                return None
            cells.append(c)
        if width is None:
            width = len(cells)
        elif len(cells) != width:
            return None
        clean.append(cells)
    if not any(c for row in clean for c in row):
        return None
    out = {'tipo': tipo, 'filas': clean}
    titulo = p.get('titulo')
    nota = p.get('nota')
    if isinstance(titulo, str) and titulo:
        out['titulo'] = titulo
    if isinstance(nota, str) and nota:
        out['nota'] = nota
    return out

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
            antiguas=w.get('formas_antiguas',[]) or []
            paradigma=index_paradigma(w.get('paradigma'))
            pcells=[c for row in (paradigma['filas'] if paradigma else []) for c in row if c]
            words.append({
                'id':w['id'],'root_id':e['id'],'root_form':e.get('form',''),'root_gloss':e.get('gloss',''),
                'letter':letter,'key':key,
                'form':w.get('form',''),'gloss':w.get('gloss',''),
                **({'emoji':w['emoji']} if w.get('emoji') else {}),
                'analysis_text':w.get('analysis_text',''),'analysis_html':w.get('analysis_html',''),
                'tags':labels(w.get('tags')),
                'refs':[r.get('id') for r in w.get('refs',[]) if r.get('id')],
                'semantic_fields':semantic_fields,'notes':notes,
                **({'formas_antiguas':antiguas} if antiguas else {}),
                **({'proviene_de':[p.get('id') for p in w.get('proviene_de',[]) if p.get('id')]} if w.get('proviene_de') else {}),
                **({'paradigma':paradigma} if paradigma else {}),
                'search':' '.join([w.get('form',''),w.get('gloss',''),e.get('form',''),e.get('gloss',''),w.get('analysis_text','')]+labels(w.get('tags'))+semantic_fields+notes+[a.get('form','') for a in antiguas]+pcells)
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