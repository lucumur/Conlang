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

def tag(label): return {'class':'generic','label':label}
def ref(mid,label): return {'id':mid,'label':label}
def word(wid,form,gloss,ah,at,refs,tags,fields,notes=None):
    w={'id':wid,'form':form,'gloss':gloss,'analysis_html':ah,'analysis_text':at,'refs':refs,'tags':[tag(x) for x in tags],'semantic_fields':fields}
    if notes: w['notes']=notes
    return w

def upsert_morph(morphs,item):
    for i,m in enumerate(morphs):
        if m.get('id')==item['id']:
            morphs[i]=item; return
    morphs.append(item)

bpath=LEX/'b.json'
b=json.loads(bpath.read_text(encoding='utf-8'))
entries=b['entries']
byid={e['id']:e for e in entries}

bar=byid['root-bar']
bar.update({'form':'*BAR-','gloss':'barrer','etymology':'Etym. Eo. balai → *BAR-','notes':[]})
bar['words']=[
word('lexeme-baras','baras','barrer, limpiar (transitivo)','BAR + <a class="morph-link" href="#morph-as">-AS</a>','BAR + -AS',[ref('morph-as','-AS')],['Predicado AS'],['movimiento','hogar']),
word('lexeme-baranos','baranos','barrer, limpiar (intransitivo)','BAR + AN (segmento no formalizado) + <a class="morph-link" href="#morph-os">-OS</a>','BAR + AN (segmento no formalizado) + -OS',[ref('morph-os','-OS')],['Predicado OS'],['movimiento','hogar']),
word('lexeme-lumbaras','lumbaras','escanear','<a class="morph-link" href="#root-lum">LUM</a> + BAR + <a class="morph-link" href="#morph-as">-AS</a>','LUM + BAR + -AS',[ref('root-lum','LUM'),ref('morph-as','-AS')],['Predicado AS'],['movimiento','objetos']),
word('lexeme-barango','barango','escoba','BAR + ANG (segmento no formalizado) + <a class="morph-link" href="#morph-o">-O</a>','BAR + ANG (segmento no formalizado) + -O',[ref('morph-o','-O')],['Inanimado O'],['objetos','hogar']),
word('lexeme-barantan','barantan','barrendero','BAR + <a class="morph-link" href="#morph-antan">-ANTAN</a>','BAR + -ANTAN',[ref('morph-antan','-ANTAN')],['Humano agentivo'],['oficios','personas','hogar']),
word('lexeme-barasma','barasma','barrendería, intendencia','BAR + ASMA (formación lexicalizada)','BAR + ASMA (formación lexicalizada)',[],['Nomen A'],['oficios','hogar','relaciones'])]

barb=byid['root-bar-b']
barb.update({'id':'root-barb','form':'*BARB-','gloss':'barba','notes':[]})
barb['words']=[
word('lexeme-barbalis','barbalis','crecer la barba','BARB + AL (segmento no formalizado) + <a class="morph-link" href="#morph-is">-IS</a>','BARB + AL (segmento no formalizado) + -IS',[ref('morph-is','-IS')],['Predicado IS'],['anatomía','cualidades']),
word('lexeme-barbol','barbol','barbón','BARB + OL (formante no formalizado)','BARB + OL (formante no formalizado)',[],['Adjetivo'],['anatomía','personas','cualidades']),
word('lexeme-lombarbin','lombarbin','viejo, sabio','LOM- (segmento no formalizado) + BARB + <a class="morph-link" href="#morph-in">-IN</a>','LOM- (segmento no formalizado) + BARB + -IN',[ref('morph-in','-IN')],['Participio animante'],['personas','edad','cualidades']),
word('lexeme-sebarbin','sebarbin','imberbe, joven','SE- (segmento no formalizado) + BARB + <a class="morph-link" href="#morph-in">-IN</a>','SE- (segmento no formalizado) + BARB + -IN',[ref('morph-in','-IN')],['Participio animante'],['personas','edad','cualidades']),
word('lexeme-barbo','barbo','barba','BARB + <a class="morph-link" href="#morph-o">-O</a>','BARB + -O',[ref('morph-o','-O')],['Inanimado O'],['anatomía','personas']),
word('lexeme-sobarbo','sobarbo','barbilla, mentón','<a class="morph-link" href="#morph-so-sub">SO-</a> + BARB + <a class="morph-link" href="#morph-o">-O</a>','SO- + BARB + -O',[ref('morph-so-sub','SO-'),ref('morph-o','-O')],['Inanimado O'],['anatomía','personas']),
word('lexeme-barben','barben','bagre','BARB + <a class="morph-link" href="#morph-en">-EN</a>','BARB + -EN',[ref('morph-en','-EN')],['Animado EN'],['animales','fauna'])]

bard={'id':'root-bard','form':'*BARD-','gloss':'borde, orilla','tags':[tag('Raiz')],'letter':'B','section':'sec-b','etymology':None,'notes':[],'row_class':'lex-root-row','words':[
word('lexeme-bardeas','bardeas','bordear','BARD + <a class="morph-link" href="#morph-eas-travel">-EAS</a>','BARD + -EAS',[ref('morph-eas-travel','-EAS')],['Predicado EAS'],['movimiento','relaciones']),
word('lexeme-bardis','bardis','colindar','BARD + <a class="morph-link" href="#morph-is">-IS</a>','BARD + -IS',[ref('morph-is','-IS')],['Predicado IS'],['relaciones','dirección']),
word('lexeme-robarda','robarda','marco, recuadro','<a class="morph-link" href="#morph-ro-2">RO-</a> + BARD + <a class="morph-link" href="#morph-a-2">-A</a>','RO- + BARD + -A',[ref('morph-ro-2','RO-'),ref('morph-a-2','-A')],['Nomen A'],['objetos','forma']),
word('lexeme-barda','barda','borde, orilla','BARD + <a class="morph-link" href="#morph-a-2">-A</a>','BARD + -A',[ref('morph-a-2','-A')],['Nomen A'],['forma','relaciones']),
word('lexeme-nurbardel','nurbardel','limítrofe','<a class="morph-link" href="#root-nur">NUR</a> + BARD + <a class="morph-link" href="#morph-el">-EL</a>','NUR + BARD + -EL',[ref('root-nur','NUR'),ref('morph-el','-EL')],['Adjetivo'],['relaciones','dirección','cualidades']),
word('lexeme-trabarda','trabarda','babor','<a class="morph-link" href="#morph-tra-behind">TRA-</a> + BARD + <a class="morph-link" href="#morph-a-2">-A</a>','TRA- + BARD + -A',[ref('morph-tra-behind','TRA-'),ref('morph-a-2','-A')],['Nomen A'],['dirección','objetos','relaciones']),
word('lexeme-manbarda','manbarda','estribor','<a class="morph-link" href="#root-man">MAN</a> + BARD + <a class="morph-link" href="#morph-a-2">-A</a>','MAN + BARD + -A',[ref('root-man','MAN'),ref('morph-a-2','-A')],['Nomen A'],['dirección','objetos','relaciones'],['MAN- «mano»: denominación interna motivada por el lado donde se encontraba el steer/timón.'])]}
entries=[e for e in entries if e.get('id')!='root-bard']
pos=next(i for i,e in enumerate(entries) if e.get('id')=='root-barb')
entries.insert(pos+1,bard)
b['entries']=entries

for e in entries:
    if e.get('id')=='root-bamb':
        for w in e.get('words',[]):
            if w.get('id')=='lexeme-bambite':
                w.update({'analysis_html':'BAMB + <a class="morph-link" href="#morph-ite-noncount">-ITE</a>','analysis_text':'BAMB + -ITE','refs':[ref('morph-ite-noncount','-ITE')]})
    if e.get('id')=='root-band':
        for w in e.get('words',[]):
            if w.get('id')=='lexeme-gxabandos':
                w.update({'analysis_html':'<a class="morph-link" href="#morph-ga-distributive">ĜA-</a> + BAND + <a class="morph-link" href="#morph-os">-OS</a>','analysis_text':'ĜA- + BAND + -OS','refs':[ref('morph-ga-distributive','ĜA-'),ref('morph-os','-OS')]})

bpath.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

mpath=LEX/'morphemes.json'
m=json.loads(mpath.read_text(encoding='utf-8'))
morphs=m['morphemes']
upsert_morph(morphs,{'id':'morph-ga-distributive','form':'*ĜA-','gloss':'derivativo distributivo, similar a trans- o dia-','tags':[tag('prefijo'),tag('distributivo')],'letter':'Ĝ','section':'sec-circ-g','etymology':None,'notes':['Atestiguado en ĝabandos. Se mantiene como morfema distinto de *ĈA- distributivo.'],'row_class':''})
upsert_morph(morphs,{'id':'morph-ite-noncount','form':'*-ITE','gloss':'derivativo que produce una forma en -E de valor no cuantificable','tags':[tag('sufijo'),tag('derivativo')],'letter':'I','section':'sec-i','etymology':None,'notes':['Atestiguado en bambite; se registra como unidad -ITE sin postular un *-IT- independiente.'],'row_class':''})
upsert_morph(morphs,{'id':'morph-eas-travel','form':'*-EAS','gloss':'transitivo relacionado con viaje o travesía','tags':[tag('sufijo'),tag('predicativo')],'letter':'E','section':'sec-e','etymology':None,'notes':['Atestiguado en bardeas.'],'row_class':''})
upsert_morph(morphs,{'id':'morph-tra-behind','form':'*TRA-','gloss':'detrás','tags':[tag('prefijo')],'letter':'T','section':'sec-t','etymology':None,'notes':['Morfema homónimo independiente de la raíz *TRA- «a través». Atestiguado en trabarda.'],'row_class':''})
mpath.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

subprocess.run(['git','add','lexico/b.json','lexico/morphemes.json'],check=True)

def labels(tags): return [t.get('label','') for t in tags or []]
roots=[]; words=[]
for letter,key in LETTER_FILES:
    data=json.loads((LEX/f'{key}.json').read_text(encoding='utf-8'))
    for e in data.get('entries',[]):
        if e.get('kind')=='other': continue
        parts=[e.get('form',''),e.get('gloss',''),e.get('etymology') or '']+labels(e.get('tags'))
        for w in e.get('words',[]):
            semantic_fields=w.get('semantic_fields',[]) or []; notes=w.get('notes',[]) or []
            parts += [w.get('form',''),w.get('gloss',''),w.get('analysis_text','')]+labels(w.get('tags'))+semantic_fields+notes
            words.append({'id':w['id'],'root_id':e['id'],'letter':letter,'key':key,'form':w.get('form',''),'gloss':w.get('gloss',''),'refs':[r.get('id') for r in w.get('refs',[]) if r.get('id')],'semantic_fields':semantic_fields,'notes':notes,'search':' '.join([w.get('form',''),w.get('gloss',''),w.get('analysis_text','')]+labels(w.get('tags'))+semantic_fields+notes)})
        roots.append({'id':e['id'],'letter':letter,'key':key,'form':e.get('form',''),'gloss':e.get('gloss',''),'tags':labels(e.get('tags')),'etymology':e.get('etymology'),'search':' '.join(parts)})
mdata=json.loads((LEX/'morphemes.json').read_text(encoding='utf-8'))
morphemes=[]
for mm in mdata.get('morphemes',[]):
    morphemes.append({'id':mm['id'],'letter':mm.get('letter',''),'form':mm.get('form',''),'gloss':mm.get('gloss',''),'tags':labels(mm.get('tags')),'search':' '.join([mm.get('form',''),mm.get('gloss','')]+labels(mm.get('tags')))})
payload={'schema_version':1,'letters':[{'section':'sec-'+key,'letter':letter,'key':key,'file':f'lexico/{key}.json'} for letter,key in LETTER_FILES],'roots':roots,'words':words,'morphemes':morphemes,'counts':{'roots':len(roots),'words':len(words),'morphemes':len(morphemes)}}
(LEX/'index.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(payload['counts'])
