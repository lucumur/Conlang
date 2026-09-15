from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
LEX = ROOT / 'lexico'

LETTER_FILES = [
    ('A','a'),('B','b'),('C','c'),('Ĉ','circ-c'),('D','d'),('E','e'),('F','f'),('G','g'),('Ĝ','circ-g'),
    ('I','i'),('J','j'),('K','k'),('L','l'),('M','m'),('N','n'),('O','o'),('P','p'),('R','r'),('S','s'),
    ('Ŝ','circ-s'),('T','t'),('Θ','theta'),('U','u'),('V','v'),('Z','z'),('Ẑ','circ-z')
]

SEMANTIC_ASSIGNMENTS = {
    "lexeme-ace": ["materiales", "geología"],
    "lexeme-agitas": ["conducta", "relaciones", "personas"],
    "lexeme-aglagen": ["aves", "fauna"],
    "lexeme-agliken": ["aves", "fauna"],
    "lexeme-agolas": ["artes escénicas", "artes", "personas"],
    "lexeme-agolistan": ["artes escénicas", "profesiones", "personas"],
    "lexeme-agolos": ["artes escénicas", "artes", "personas"],
    "lexeme-agolura": ["artes escénicas", "artes"],
    "lexeme-agos": ["conducta", "personas"],
    "lexeme-agura": ["conducta", "cualidades"],
    "lexeme-agxeta": ["tiempo", "calendario"],
    "lexeme-agxeva": ["edad", "tiempo"],
    "lexeme-agxil": ["edad", "estado"],
    "lexeme-agxin": ["edad", "estado"],
    "lexeme-agxos": ["edad", "envejecimiento", "procesos"],
    "lexeme-agxoton": ["edad", "personas"],
    "lexeme-ajha": ["procesos", "cambio"],
    "lexeme-ajhan": ["personas", "procesos"],
    "lexeme-ajhas": ["procesos", "transformación"],
    "lexeme-ajhes": ["estado", "estado resultante"],
    "lexeme-ajhos": ["procesos", "transformación", "cambio de estado"],
    "lexeme-ajhumezha": ["cualidades", "propiedades"],
    "lexeme-ajhumur": ["cualidades", "descripción"],
    "lexeme-alantaf": ["movimiento", "dirección", "espacio"],
    "lexeme-alantos": ["movimiento", "dirección", "espacio"],
    "lexeme-alantur": ["dirección", "espacio", "cualidades"],
    "lexeme-alba": ["palidez", "colores", "apariencia"],
    "lexeme-albam": ["tiempo", "inicio"],
    "lexeme-albis": ["colores", "apariencia"],
    "lexeme-albjal": ["geografía", "lugares"],
    "lexeme-albjol": ["colores", "apariencia"],
    "lexeme-albjon": ["mitología", "personas"],
    "lexeme-albucesta": ["salud", "congénito", "palidez"],
    "lexeme-alma": ["religión", "mitología"],
    "lexeme-almas": ["procesos", "vigor"],
    "lexeme-almen": ["animales", "fauna"],
    "lexeme-almidaj": ["emociones", "vigor", "deseo"],
    "lexeme-almos": ["emociones", "vigor"],
    "lexeme-altaf": ["dirección", "espacio"],
    "lexeme-altala": ["geografía", "magnitud", "espacio"],
    "lexeme-altezha": ["magnitud", "cualidades"],
    "lexeme-ambre": ["materiales", "colores"],
    "lexeme-ambrol": ["colores", "apariencia"],
    "lexeme-amerkal": ["geografía", "continentes"],
    "lexeme-amerkel": ["gentilicios", "geografía", "descripción"],
    "lexeme-amerkin": ["gentilicios", "personas", "geografía"],
    "lexeme-andaglen": ["aves", "fauna", "montañas"],
    "lexeme-angla": ["habla", "lenguaje", "comunicación"],
    "lexeme-anglaf": ["lenguaje", "descripción"],
    "lexeme-angler": ["gentilicios", "descripción", "geografía"],
    "lexeme-angleral": ["geografía", "lugares"],
    "lexeme-angleron": ["gentilicios", "personas", "geografía"],
    "lexeme-anglivocon": ["personas", "habla", "lenguaje"],
    "lexeme-angloni": ["gentilicios", "personas", "geografía"],
    "lexeme-ango": ["geometría", "forma"],
    "lexeme-angudol": ["geometría", "forma", "cualidades"],
    "lexeme-anksa": ["salud", "estado"],
    "lexeme-anksas": ["salud", "procesos"],
    "lexeme-anksema": ["emociones", "salud"],
    "lexeme-anksidaj": ["emociones", "salud"],
    "lexeme-anksos": ["salud", "procesos"],
    "lexeme-antacom": ["jerarquía", "primordialidad"],
    "lexeme-antaf": ["dirección", "espacio"],
    "lexeme-antajur": ["tiempo", "calendario"],
    "lexeme-antam": ["tiempo", "dirección"],
    "lexeme-antevada": ["antigüedad", "tiempo"],
    "lexeme-antevon": ["antigüedad", "personas", "tiempo"],
    "lexeme-antevur": ["antigüedad", "tiempo", "cualidades"],
    "lexeme-antur": ["tiempo", "dirección"],
    "lexeme-arbadal": ["botánica", "árboles", "lugares"],
    "lexeme-arbifas": ["procesos", "cambio", "propiedades físicas"],
    "lexeme-arbigos": ["cambio de estado", "propiedades físicas", "procesos"],
    "lexeme-arbiko": ["botánica", "vegetales"],
    "lexeme-arbikrona": ["botánica", "árboles", "partes"],
    "lexeme-arbo": ["botánica", "árboles"],
    "lexeme-arbol": ["cualidades", "propiedades físicas"],
    "lexeme-arbolda": ["cualidades", "propiedades físicas"],
    "lexeme-arzas": ["procesos", "forma", "objetos"],
    "lexeme-arziko": ["objetos", "partes", "forma"],
    "lexeme-arzo": ["anatomía", "partes", "forma"],
    "lexeme-arzoro": ["anatomía", "partes"],
    "lexeme-arzos": ["procesos", "forma", "objetos"],
    "lexeme-arzur": ["propiedades físicas", "cualidades", "forma"],
    "lexeme-asper": ["cualidades", "propiedades físicas", "descripción"],
    "lexeme-asprago": ["alimentación", "vegetales", "botánica"],
    "lexeme-astorbo": ["cielo", "naturaleza", "espacio"],
    "lexeme-astriko": ["anatomía", "partes", "salud"],
    "lexeme-astrila": ["cielo", "apariencia", "naturaleza"],
    "lexeme-astrilos": ["apariencia", "procesos", "cielo"],
    "lexeme-astro": ["cielo", "naturaleza", "espacio"],
    "lexeme-athla": ["deportes", "interacción", "procesos"],
    "lexeme-athlisma": ["deportes", "disciplinas"],
    "lexeme-athlistan": ["deportes", "personas", "profesiones"],
    "lexeme-athlistel": ["deportes", "cualidades", "descripción"],
    "lexeme-athlos": ["deportes", "interacción", "personas"],
    "lexeme-beleblira": ["estado", "relaciones", "procesos"],
    "lexeme-bonagaj": ["conducta", "relaciones", "cualidades"],
    "lexeme-bonalmor": ["conducta", "cualidades", "personas"],
    "lexeme-brustanksa": ["salud", "anatomía"],
    "lexeme-brustanksol": ["salud", "anatomía", "cualidades"],
    "lexeme-coalma": ["cristianismo", "religión", "divinidades"],
    "lexeme-eblik": ["gramática", "estado"],
    "lexeme-eblir": ["cualidades", "estado"],
    "lexeme-eblis": ["estado", "procesos", "cualidades"],
    "lexeme-eblol": ["cualidades", "propiedades"],
    "lexeme-eblonas": ["procesos", "cualidades", "estado"],
    "lexeme-eblos": ["cualidades", "propiedades", "estado"],
    "lexeme-eblura": ["cualidades", "propiedades"],
    "lexeme-fisurir": ["alimentación", "conservación", "estado resultante"],
    "lexeme-gadrango": ["geometría", "forma"],
    "lexeme-ginkango": ["geometría", "forma"],
    "lexeme-kolanksa": ["salud", "procesos"],
    "lexeme-kolanksas": ["salud", "procesos"],
    "lexeme-lontagxeva": ["tiempo", "duración"],
    "lexeme-lontagxol": ["tiempo", "duración", "cualidades"],
    "lexeme-malalmor": ["conducta", "cualidades", "personas"],
    "lexeme-maleblonir": ["personas", "salud", "cualidades"],
    "lexeme-mejeblira": ["estado", "cualidades", "procesos"],
    "lexeme-natarbo": ["botánica", "árboles", "cristianismo"],
    "lexeme-nejhas": ["procesos", "cambio"],
    "lexeme-nujalmas": ["salud", "procesos", "vigor"],
    "lexeme-nujalmida": ["salud", "procesos", "vigor"],
    "lexeme-oarza": ["relaciones", "interacción", "comunicación"],
    "lexeme-oarzos": ["relaciones", "interacción", "cualidades"],
    "lexeme-oastropa": ["movimiento", "interacción", "procesos"],
    "lexeme-oastropos": ["movimiento", "interacción", "procesos"],
    "lexeme-oathlos": ["deportes", "interacción", "personas"],
    "lexeme-opajha": ["procesos", "interacción", "cambio"],
    "lexeme-opantur": ["relaciones", "dirección", "cualidades"],
    "lexeme-orkaglen": ["aves", "fauna"],
    "lexeme-ozastren": ["animales acuáticos", "fauna", "acuáticos"],
    "lexeme-soalbol": ["colores", "apariencia", "palidez"],
    "lexeme-surer": ["ácido-base", "cualidades", "alimentación"],
    "lexeme-surigos": ["ácido-base", "procesos", "cambio de estado"],
    "lexeme-surne": ["alimentación", "ácido-base", "líquidos"],
    "lexeme-suruda": ["ácido-base", "propiedades", "cualidades"],
    "lexeme-timanksema": ["emociones", "salud"],
    "lexeme-tiralbiston": ["montañas", "deportes", "personas"],
    "lexeme-zetikambre": ["materiales", "sustancias", "animales acuáticos"]
}

def labels(tags):
    return [t.get('label','') for t in tags or []]

# Primero reunimos el vocabulario semántico ya canónico.
existing_vocab=set()
for _,key in LETTER_FILES:
    data=json.loads((LEX/f'{key}.json').read_text(encoding='utf-8'))
    for e in data.get('entries',[]):
        for w in e.get('words',[]):
            existing_vocab.update(w.get('semantic_fields',[]) or [])

proposed_vocab={field for fields in SEMANTIC_ASSIGNMENTS.values() for field in fields}
unknown=sorted(proposed_vocab-existing_vocab)
if unknown:
    raise RuntimeError(f'Campos semánticos nuevos no autorizados: {unknown}')

matched=set()
applied=0
changed_files=[]
for _,key in LETTER_FILES:
    path=LEX/f'{key}.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    changed=False
    for e in data.get('entries',[]):
        for w in e.get('words',[]):
            wid=w.get('id')
            if wid in SEMANTIC_ASSIGNMENTS:
                matched.add(wid)
                if not (w.get('semantic_fields',[]) or []):
                    w['semantic_fields']=SEMANTIC_ASSIGNMENTS[wid]
                    applied += 1
                    changed=True
    if changed:
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        changed_files.append(key)

unmatched=sorted(set(SEMANTIC_ASSIGNMENTS)-matched)
if unmatched:
    raise RuntimeError(f'IDs de palabras no encontrados: {unmatched}')

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
print('SEMANTIC_FILL_SUMMARY', json.dumps({'assignments':len(SEMANTIC_ASSIGNMENTS),'applied':applied,'changed_files':changed_files,'remaining_invalid':len(remaining)},ensure_ascii=False))
print(payload['counts'])
