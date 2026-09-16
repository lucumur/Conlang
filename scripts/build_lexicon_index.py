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

# Migración puntual BAMB/BAND y -UM colectivo.
bpath=LEX/'b.json'
bdata=json.loads(bpath.read_text(encoding='utf-8'))
byid={e.get('id'):e for e in bdata.get('entries',[])}
bamb=byid.get('root-bamb')
band=byid.get('root-band')
if bamb is None or band is None:
    raise RuntimeError('No se encontraron root-bamb/root-band')

bamb['words']=[
    {
      'id':'lexeme-bambo','form':'bambo','gloss':'bambú',
      'analysis_html':'BAMB (forma léxica nominal)',
      'analysis_text':'BAMB (forma léxica nominal)','refs':[],
      'tags':[{'class':'generic','label':'Nomen'}],
      'semantic_fields':['botánica','vegetales']
    },
    {
      'id':'lexeme-bambite','form':'bambite','gloss':'madera de bambú',
      'analysis_html':'BAMB + ITE (segmento no formalizado)',
      'analysis_text':'BAMB + ITE (segmento no formalizado)','refs':[],
      'tags':[{'class':'generic','label':'Nomen'}],
      'semantic_fields':['materiales','botánica']
    }
]

band['words']=[
    {
      'id':'lexeme-gxabandos','form':'ĝabandos','gloss':'faccionarse',
      'analysis_html':'ĜA- (segmento no formalizado) + BAND + <a class="morph-link" href="#morph-os">-OS</a>',
      'analysis_text':'ĜA- (segmento no formalizado) + BAND + -OS',
      'refs':[{'id':'morph-os','label':'-OS'}],
      'tags':[{'class':'generic','label':'Predicado OS'}],
      'semantic_fields':['procesos','relaciones','personas']
    },
    {
      'id':'lexeme-obandos','form':'obandos','gloss':'agruparse',
      'analysis_html':'<a class="morph-link" href="#morph-o-mutual">O-</a> + BAND + <a class="morph-link" href="#morph-os">-OS</a>',
      'analysis_text':'O- + BAND + -OS',
      'refs':[{'id':'morph-o-mutual','label':'O-'},{'id':'morph-os','label':'-OS'}],
      'tags':[{'class':'generic','label':'Predicado OS'}],
      'semantic_fields':['procesos','relaciones','interacción']
    },
    {
      'id':'lexeme-bandum','form':'bandum','gloss':'banda, grupo, tropa',
      'analysis_html':'BAND + <a class="morph-link" href="#morph-um-collective">-UM</a>',
      'analysis_text':'BAND + -UM',
      'refs':[{'id':'morph-um-collective','label':'-UM'}],
      'tags':[{'class':'generic','label':'Colectivo'}],
      'semantic_fields':['personas','relaciones']
    },
    {
      'id':'lexeme-parbanda','form':'parbanda','gloss':'facción, bando',
      'analysis_html':'<a class="morph-link" href="#root-par">PAR</a> + BAND + <a class="morph-link" href="#morph-a-2">-A</a>',
      'analysis_text':'PAR + BAND + -A',
      'refs':[{'id':'root-par','label':'PAR'},{'id':'morph-a-2','label':'-A'}],
      'tags':[{'class':'generic','label':'Nomen A'}],
      'semantic_fields':['relaciones','interacción']
    }
]
bpath.write_text(json.dumps(bdata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

mpath=LEX/'morphemes.json'
mdata=json.loads(mpath.read_text(encoding='utf-8'))
mid='morph-um-collective'
m=next((x for x in mdata.get('morphemes',[]) if x.get('id')==mid),None)
entry={
    'id':mid,'form':'*-UM','gloss':'colectivo',
    'tags':[{'class':'generic','label':'sufijo'},{'class':'generic','label':'colectivo'}],
    'letter':'U','section':'sec-u','etymology':None,
    'notes':['Morfema colectivo canónico. Atestiguado en bandum «banda, grupo, tropa». Se distingue del homónimo *-UM- «tendente».'],
    'row_class':''
}
if m is None:
    mdata.setdefault('morphemes',[]).append(entry)
else:
    m.update(entry)
mpath.write_text(json.dumps(mdata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

subprocess.run(['git','config','user.name','ChatGPT'],check=True)
subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],check=True)
subprocess.run(['git','add','lexico/b.json','lexico/morphemes.json'],check=True)
if subprocess.run(['git','diff','--cached','--quiet']).returncode != 0:
    subprocess.run(['git','commit','-m','Completar BAMB y BAND [skip ci]'],check=True)
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
