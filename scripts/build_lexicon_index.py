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

changed = False

# --- Migración canónica BAT y morfemas asociados ---
b_path = LEX / 'b.json'
b = load_json(b_path)
before_b = json.dumps(b, ensure_ascii=False, sort_keys=True)
bat = entry_by_id(b, 'root-bat')
bat['gloss'] = 'tumbar, golpear hasta tumbar'
bat['notes'] = []
bat['row_class'] = 'lex-root-row'
bat['words'] = [
    {
        'id':'lexeme-batas','form':'batas','gloss':'tumbar, taclear',
        'analysis_html':'BAT + <a class="morph-link" href="#morph-as">-AS</a>',
        'analysis_text':'BAT + -AS','refs':[{'id':'morph-as','label':'-AS'}],
        'tags':[{'class':'generic','label':'Predicado AS'}],
        'semantic_fields':['movimiento','deportes']
    },
    {
        'id':'lexeme-bata','form':'bata','gloss':'tacleo',
        'analysis_html':'BAT + <a class="morph-link" href="#morph-a-2">-A</a>',
        'analysis_text':'BAT + -A','refs':[{'id':'morph-a-2','label':'-A'}],
        'tags':[{'class':'generic','label':'Nomen A'}],
        'semantic_fields':['deportes','movimiento']
    },
    {
        'id':'lexeme-bato','form':'bato','gloss':'bate, mazo',
        'analysis_html':'BAT + <a class="morph-link" href="#morph-o">-O</a>',
        'analysis_text':'BAT + -O','refs':[{'id':'morph-o','label':'-O'}],
        'tags':[{'class':'generic','label':'Inanimado O'}],
        'semantic_fields':['objetos','deportes']
    },
    {
        'id':'lexeme-sobatir','form':'sobatir','gloss':'tumbado, prono, bocabajo',
        'analysis_html':'<a class="morph-link" href="#morph-so-sub">SO-</a> + BAT + <a class="morph-link" href="#morph-ir-reservative">-IR</a>',
        'analysis_text':'SO- + BAT + -IR','refs':[{'id':'morph-so-sub','label':'SO-'},{'id':'morph-ir-reservative','label':'-IR'}],
        'tags':[{'class':'generic','label':'Resultativo'}],
        'semantic_fields':['anatomía','cualidades']
    },
    {
        'id':'lexeme-batakas','form':'batakas','gloss':'abatir, atacar',
        'analysis_html':'BAT + <a class="morph-link" href="#morph-ak-augmentative">-AK-</a> + <a class="morph-link" href="#morph-as">-AS</a>',
        'analysis_text':'BAT + -AK- + -AS','refs':[{'id':'morph-ak-augmentative','label':'-AK-'},{'id':'morph-as','label':'-AS'}],
        'tags':[{'class':'generic','label':'Predicado AS'}],
        'semantic_fields':['movimiento','relaciones','procesos']
    },
    {
        'id':'lexeme-bataka','form':'bataka','gloss':'ataque',
        'analysis_html':'BAT + <a class="morph-link" href="#morph-ak-augmentative">-AK-</a> + <a class="morph-link" href="#morph-a-2">-A</a>',
        'analysis_text':'BAT + -AK- + -A','refs':[{'id':'morph-ak-augmentative','label':'-AK-'},{'id':'morph-a-2','label':'-A'}],
        'tags':[{'class':'generic','label':'Nomen A'}],
        'semantic_fields':['movimiento','relaciones','procesos']
    },
    {
        'id':'lexeme-batolas','form':'batolas','gloss':'derrocar',
        'analysis_html':'BAT + <a class="morph-link" href="#morph-ol-perfective">-OL-</a> + <a class="morph-link" href="#morph-as">-AS</a>',
        'analysis_text':'BAT + -OL- + -AS','refs':[{'id':'morph-ol-perfective','label':'-OL-'},{'id':'morph-as','label':'-AS'}],
        'tags':[{'class':'generic','label':'Predicado AS'}],
        'semantic_fields':['relaciones','procesos','movimiento']
    },
    {
        'id':'lexeme-batolis','form':'batolis','gloss':'estar abatido, completamente cansado, rendido',
        'analysis_html':'BAT + <a class="morph-link" href="#morph-ol-perfective">-OL-</a> + <a class="morph-link" href="#morph-is">-IS</a>',
        'analysis_text':'BAT + -OL- + -IS','refs':[{'id':'morph-ol-perfective','label':'-OL-'},{'id':'morph-is','label':'-IS'}],
        'tags':[{'class':'generic','label':'Predicado IS'}],
        'semantic_fields':['personas','cualidades','procesos']
    },
    {
        'id':'lexeme-batola','form':'batola','gloss':'derrocamiento, abatimiento',
        'analysis_html':'BAT + <a class="morph-link" href="#morph-ol-perfective">-OL-</a> + <a class="morph-link" href="#morph-a-2">-A</a>',
        'analysis_text':'BAT + -OL- + -A','refs':[{'id':'morph-ol-perfective','label':'-OL-'},{'id':'morph-a-2','label':'-A'}],
        'tags':[{'class':'generic','label':'Nomen A'}],
        'semantic_fields':['relaciones','procesos']
    },
    {
        'id':'lexeme-bobatlas','form':'bobatlas','gloss':'esgrimir en duelo, combatir',
        'analysis_html':'BO (segmento no formalizado) + BAT + L (extensión lexicalizada) + <a class="morph-link" href="#morph-as">-AS</a>',
        'analysis_text':'BO (segmento no formalizado) + BAT + L (extensión lexicalizada) + -AS','refs':[{'id':'morph-as','label':'-AS'}],
        'tags':[{'class':'generic','label':'Predicado AS'}],
        'semantic_fields':['deportes','movimiento','relaciones']
    },
    {
        'id':'lexeme-bobatla','form':'bobatla','gloss':'esgrima, duelo',
        'analysis_html':'BO (segmento no formalizado) + BAT + L (extensión lexicalizada) + <a class="morph-link" href="#morph-a-2">-A</a>',
        'analysis_text':'BO (segmento no formalizado) + BAT + L (extensión lexicalizada) + -A','refs':[{'id':'morph-a-2','label':'-A'}],
        'tags':[{'class':'generic','label':'Nomen A'}],
        'semantic_fields':['deportes','movimiento','relaciones']
    },
    {
        'id':'lexeme-batlur','form':'batlur','gloss':'batalloso, difícil',
        'analysis_html':'BAT + LUR (formación lexicalizada; no se identifica automáticamente con *-UR superlativo)',
        'analysis_text':'BAT + LUR (formación lexicalizada; no se identifica automáticamente con *-UR superlativo)','refs':[],
        'tags':[{'class':'generic','label':'Adjetivo'}],
        'semantic_fields':['cualidades','relaciones']
    },
    {
        'id':'lexeme-batlanos','form':'batlanos','gloss':'combatir, guerrillear',
        'analysis_html':'BAT + L (extensión lexicalizada) + <a class="morph-link" href="#morph-an">-AN</a> + <a class="morph-link" href="#morph-os">-OS</a>',
        'analysis_text':'BAT + L (extensión lexicalizada) + -AN + -OS','refs':[{'id':'morph-an','label':'-AN'},{'id':'morph-os','label':'-OS'}],
        'tags':[{'class':'generic','label':'Predicado OS'}],
        'semantic_fields':['relaciones','movimiento','procesos']
    },
    {
        'id':'lexeme-batlana','form':'batlana','gloss':'combate, batalla',
        'analysis_html':'BAT + L (extensión lexicalizada) + <a class="morph-link" href="#morph-an">-AN</a> + <a class="morph-link" href="#morph-a-2">-A</a>',
        'analysis_text':'BAT + L (extensión lexicalizada) + -AN + -A','refs':[{'id':'morph-an','label':'-AN'},{'id':'morph-a-2','label':'-A'}],
        'tags':[{'class':'generic','label':'Nomen A'}],
        'semantic_fields':['relaciones','movimiento','procesos']
    },
    {
        'id':'lexeme-batlantan','form':'batlantan','gloss':'combatiente, guerrero',
        'analysis_html':'BAT + L (extensión lexicalizada) + <a class="morph-link" href="#morph-antan">-ANTAN</a>',
        'analysis_text':'BAT + L (extensión lexicalizada) + -ANTAN','refs':[{'id':'morph-antan','label':'-ANTAN'}],
        'tags':[{'class':'generic','label':'Humano agentivo'}],
        'semantic_fields':['personas','relaciones','movimiento']
    },
    {
        'id':'lexeme-abatas','form':'abatas','gloss':'batear',
        'analysis_html':'<a class="morph-link" href="#morph-a-instrumental">A-</a> + BAT + <a class="morph-link" href="#morph-as">-AS</a>',
        'analysis_text':'A- + BAT + -AS','refs':[{'id':'morph-a-instrumental','label':'A-'},{'id':'morph-as','label':'-AS'}],
        'tags':[{'class':'generic','label':'Predicado AS'}],
        'semantic_fields':['deportes','movimiento','objetos']
    },
    {
        'id':'lexeme-abata','form':'abata','gloss':'bateo',
        'analysis_html':'<a class="morph-link" href="#morph-a-instrumental">A-</a> + BAT + <a class="morph-link" href="#morph-a-2">-A</a>',
        'analysis_text':'A- + BAT + -A','refs':[{'id':'morph-a-instrumental','label':'A-'},{'id':'morph-a-2','label':'-A'}],
        'tags':[{'class':'generic','label':'Nomen A'}],
        'semantic_fields':['deportes','movimiento','objetos']
    },
    {
        'id':'lexeme-abatitas','form':'abatitas','gloss':'batir',
        'analysis_html':'<a class="morph-link" href="#morph-a-instrumental">A-</a> + BAT + <a class="morph-link" href="#morph-it-frequentative">-IT-</a> + <a class="morph-link" href="#morph-as">-AS</a>',
        'analysis_text':'A- + BAT + -IT- + -AS','refs':[{'id':'morph-a-instrumental','label':'A-'},{'id':'morph-it-frequentative','label':'-IT-'},{'id':'morph-as','label':'-AS'}],
        'tags':[{'class':'generic','label':'Predicado AS'}],
        'semantic_fields':['procesos','movimiento','objetos']
    },
    {
        'id':'lexeme-batitro','form':'batitro','gloss':'batidora',
        'analysis_html':'BAT + <a class="morph-link" href="#morph-it-frequentative">-IT-</a> + RO (formante lexicalizado; no se identifica con *-RO masculino)',
        'analysis_text':'BAT + -IT- + RO (formante lexicalizado)','refs':[{'id':'morph-it-frequentative','label':'-IT-'}],
        'tags':[{'class':'generic','label':'Nomen'}],
        'semantic_fields':['objetos','hogar','procesos']
    },
    {
        'id':'lexeme-abatita','form':'abatita','gloss':'batimiento',
        'analysis_html':'<a class="morph-link" href="#morph-a-instrumental">A-</a> + BAT + <a class="morph-link" href="#morph-it-frequentative">-IT-</a> + <a class="morph-link" href="#morph-a-2">-A</a>',
        'analysis_text':'A- + BAT + -IT- + -A','refs':[{'id':'morph-a-instrumental','label':'A-'},{'id':'morph-it-frequentative','label':'-IT-'},{'id':'morph-a-2','label':'-A'}],
        'tags':[{'class':'generic','label':'Nomen A'}],
        'semantic_fields':['procesos','movimiento','objetos']
    },
    {
        'id':'lexeme-obatitos','form':'obatitos','gloss':'batirse (coire; uso eufemístico)',
        'analysis_html':'<a class="morph-link" href="#morph-o-mutual">O-</a> + BAT + <a class="morph-link" href="#morph-it-frequentative">-IT-</a> + <a class="morph-link" href="#morph-os">-OS</a>',
        'analysis_text':'O- + BAT + -IT- + -OS','refs':[{'id':'morph-o-mutual','label':'O-'},{'id':'morph-it-frequentative','label':'-IT-'},{'id':'morph-os','label':'-OS'}],
        'tags':[{'class':'generic','label':'Predicado OS'}],
        'semantic_fields':['sexualidad','interacción','movimiento']
    },
    {
        'id':'lexeme-gxabatas','form':'ĝabatas','gloss':'pasar a alguien',
        'analysis_html':'<a class="morph-link" href="#morph-ga-distributive">ĜA-</a> + BAT + <a class="morph-link" href="#morph-as">-AS</a>',
        'analysis_text':'ĜA- + BAT + -AS','refs':[{'id':'morph-ga-distributive','label':'ĜA-'},{'id':'morph-as','label':'-AS'}],
        'tags':[{'class':'generic','label':'Predicado AS'}],
        'semantic_fields':['movimiento','relaciones','personas']
    },
    {
        'id':'lexeme-chabatas','form':'ĉabatas','gloss':'arrebatar',
        'analysis_html':'<a class="morph-link" href="#morph-ca">ĈA-</a> + BAT + <a class="morph-link" href="#morph-as">-AS</a>',
        'analysis_text':'ĈA- + BAT + -AS','refs':[{'id':'morph-ca','label':'ĈA-'},{'id':'morph-as','label':'-AS'}],
        'tags':[{'class':'generic','label':'Predicado AS'}],
        'semantic_fields':['movimiento','relaciones','objetos']
    },
    {
        'id':'lexeme-chabata','form':'ĉabata','gloss':'arrebato',
        'analysis_html':'<a class="morph-link" href="#morph-ca">ĈA-</a> + BAT + <a class="morph-link" href="#morph-a-2">-A</a>',
        'analysis_text':'ĈA- + BAT + -A','refs':[{'id':'morph-ca','label':'ĈA-'},{'id':'morph-a-2','label':'-A'}],
        'tags':[{'class':'generic','label':'Nomen A'}],
        'semantic_fields':['movimiento','relaciones','objetos']
    }
]
if json.dumps(b, ensure_ascii=False, sort_keys=True) != before_b:
    save_json(b_path, b)
    changed = True

m_path = LEX / 'morphemes.json'
mdata = load_json(m_path)
before_m = json.dumps(mdata, ensure_ascii=False, sort_keys=True)
morphs = mdata.setdefault('morphemes', [])
byid = {m.get('id'):m for m in morphs}

def upsert(mid, form, gloss, letter, label='sufijo', notes=None):
    obj = {
        'id':mid,'form':form,'gloss':gloss,
        'tags':[{'class':'generic','label':label}],
        'letter':letter,'section':'sec-'+({'Ĉ':'circ-c','Ĝ':'circ-g','Ŝ':'circ-s','Ẑ':'circ-z','Θ':'theta'}.get(letter,letter.lower())),
        'etymology':None,'notes':notes or [],'row_class':''
    }
    if mid in byid:
        byid[mid].update(obj)
    else:
        morphs.append(obj); byid[mid]=obj

upsert('morph-a-instrumental','*A-','instrumental; ejecutar la acción usando algo o una herramienta como medio','A','prefijo')
upsert('morph-ak-augmentative','*-AK-','aumentativo verbal; amplía el alcance o la extensión de la acción','A','sufijo')
upsert('morph-ol-perfective','*-OL-','perfectivo; acción completamente terminada, con resultado pleno','O','sufijo')
upsert('morph-it-frequentative','*-IT-','frecuentativo; acción repetida o iterada','I','sufijo')
if 'morph-ca' in byid:
    byid['morph-ca']['gloss'] = 'echar, quitar'
    byid['morph-ca']['tags'] = [{'class':'generic','label':'prefijo'}]
    byid['morph-ca']['notes'] = []
if 'morph-ite-noncount' in byid:
    byid['morph-ite-noncount']['notes'] = []
if json.dumps(mdata, ensure_ascii=False, sort_keys=True) != before_m:
    save_json(m_path, mdata)
    changed = True

# --- Generación normal del índice ---
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
    staged=subprocess.run(['git','diff','--cached','--quiet'])
    if staged.returncode != 0:
        subprocess.run(['git','commit','-m','Canonizar familia BAT y morfemas asociados'], check=True)
        subprocess.run(['git','push'], check=True)
