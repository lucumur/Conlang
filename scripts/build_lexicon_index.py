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

bpath=LEX/'b.json'
bdata=json.loads(bpath.read_text(encoding='utf-8'))
root=next((e for e in bdata.get('entries',[]) if e.get('id')=='root-bald'),None)
if root is None:
    raise RuntimeError('root-bald no encontrado')
root['words']=[
    {
      'id':'lexeme-baldaf','form':'baldaf','gloss':'pronto, en breve, enseguida',
      'analysis_html':'BALD + <a class="morph-link" href="#morph-af">-AF</a>',
      'analysis_text':'BALD + -AF','refs':[{'id':'morph-af','label':'-AF'}],
      'tags':[{'class':'generic','label':'Adverbio AF'}],
      'semantic_fields':['tiempo','dirección']
    },
    {
      'id':'lexeme-balder','form':'balder','gloss':'early, pronto, temprano',
      'analysis_html':'BALD + <a class="morph-link" href="#morph-er">-ER</a>',
      'analysis_text':'BALD + -ER','refs':[{'id':'morph-er','label':'-ER'}],
      'tags':[{'class':'generic','label':'Adjetivo ER'}],
      'semantic_fields':['tiempo','cualidades','descripción']
    },
    {
      'id':'lexeme-jobaldol','form':'jobaldol','gloss':'puntual',
      'analysis_html':'JO (segmento no formalizado) + BALD + <a class="morph-link" href="#morph-ol-2">-OL</a>',
      'analysis_text':'JO (segmento no formalizado) + BALD + -OL','refs':[{'id':'morph-ol-2','label':'-OL'}],
      'tags':[{'class':'generic','label':'Adjetivo OL'}],
      'semantic_fields':['tiempo','cualidades','conducta']
    },
    {
      'id':'lexeme-penbaldik','form':'penbaldik','gloss':'ya casi',
      'analysis_html':'<a class="morph-link" href="#root-pen">PEN</a> + BALD + <a class="morph-link" href="#morph-ik">-IK-</a>',
      'analysis_text':'PEN + BALD + -IK-','refs':[{'id':'root-pen','label':'PEN'},{'id':'morph-ik','label':'-IK-'}],
      'tags':[{'class':'generic','label':'Adverbio'}],
      'semantic_fields':['tiempo','estado']
    },
    {
      'id':'lexeme-baldamur','form':'baldamur','gloss':'próximo',
      'analysis_html':'BALD + <a class="morph-link" href="#morph-am">-AM</a> + <a class="morph-link" href="#morph-ur-3">-UR</a>',
      'analysis_text':'BALD + -AM + -UR','refs':[{'id':'morph-am','label':'-AM'},{'id':'morph-ur-3','label':'-UR'}],
      'tags':[{'class':'generic','label':'Adjetivo UR'}],
      'semantic_fields':['tiempo','dirección','cualidades']
    },
    {
      'id':'lexeme-baldamos','form':'baldamos','gloss':'aproximarse',
      'analysis_html':'BALD + <a class="morph-link" href="#morph-am">-AM</a> + <a class="morph-link" href="#morph-os">-OS</a>',
      'analysis_text':'BALD + -AM + -OS','refs':[{'id':'morph-am','label':'-AM'},{'id':'morph-os','label':'-OS'}],
      'tags':[{'class':'generic','label':'Predicado OS'}],
      'semantic_fields':['movimiento','dirección','tiempo']
    },
    {
      'id':'lexeme-baldamik','form':'baldamik','gloss':'aproximadamente',
      'analysis_html':'BALD + <a class="morph-link" href="#morph-am">-AM</a> + <a class="morph-link" href="#morph-ik">-IK-</a>',
      'analysis_text':'BALD + -AM + -IK-','refs':[{'id':'morph-am','label':'-AM'},{'id':'morph-ik','label':'-IK-'}],
      'tags':[{'class':'generic','label':'Adverbio'}],
      'semantic_fields':['magnitud','comparativos','gramática']
    }
]
bpath.write_text(json.dumps(bdata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
subprocess.run(['git','config','user.name','ChatGPT'],check=True)
subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],check=True)
subprocess.run(['git','add','lexico/b.json'],check=True)
subprocess.run(['git','commit','-m','Completar familia BALD [skip ci]'],check=True)
subprocess.run(['git','push'],check=True)

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
