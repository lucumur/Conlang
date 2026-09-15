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

def canonicalize_new_morphology():
    changed_paths=[]

    # Morfemas: -ONTON, -ANTAN y -ĈA. Se conserva -ONTAN como morfema distinto.
    mpath=LEX/'morphemes.json'
    mdata=json.loads(mpath.read_text(encoding='utf-8'))
    morphs=mdata.get('morphemes',[])
    byid={m.get('id'):m for m in morphs}
    additions=[
        {
            'id':'morph-onton','form':'*-ONTON','gloss':'extensión reduplicada de -ON',
            'tags':[{'class':'generic','label':'sufijo'},{'class':'generic','label':'extensión reduplicada'}],
            'letter':'O','section':'sec-o','etymology':None,
            'notes':['Canónico. Deriva del -ON humano mediante una formación parcialmente reduplicada. Atestiguado en balonton «bailarín». Distinto de -ONTAN, derivado especializado de -ONAS.'],
            'row_class':''
        },
        {
            'id':'morph-antan','form':'*-ANTAN','gloss':'extensión reduplicada de -AN',
            'tags':[{'class':'generic','label':'sufijo'},{'class':'generic','label':'extensión reduplicada'}],
            'letter':'A','section':'sec-a','etymology':None,
            'notes':['Canónico. Deriva del -AN humano agentivo mediante una formación parcialmente reduplicada. Atestiguado en bakantan «panadero» y arcantan «rey, dirigente».'],
            'row_class':''
        },
        {
            'id':'morph-cha-disease','form':'*-ĈA','gloss':'enfermedad, afección',
            'tags':[{'class':'generic','label':'sufijo'},{'class':'generic','label':'enfermedad'}],
            'letter':'Ĉ','section':'sec-circ-c','etymology':None,
            'notes':['Canónico. Atestiguado en virbalĉa «balanitis».'],
            'row_class':''
        }
    ]
    for m in additions:
        if m['id'] not in byid:
            morphs.append(m)
    if 'morph-ontan' in byid:
        note='Distinto de *-ONTON, extensión reduplicada de -ON.'
        notes=byid['morph-ontan'].setdefault('notes',[])
        if note not in notes:
            notes.append(note)
    mpath.write_text(json.dumps(mdata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    changed_paths.append('lexico/morphemes.json')

    # B: reanalizar BAL, BAK y la enfermedad en -ĈA.
    bpath=LEX/'b.json'
    bdata=json.loads(bpath.read_text(encoding='utf-8'))
    entries={e.get('id'):e for e in bdata.get('entries',[])}
    if 'root-bal' in entries:
        words={w.get('id'):w for w in entries['root-bal'].get('words',[])}
        w=words.get('lexeme-balonton')
        if w:
            w['analysis_html']='BAL + <a class="morph-link" href="#morph-onton">-ONTON</a>'
            w['analysis_text']='BAL + -ONTON'
            w['refs']=[{'id':'morph-onton','label':'-ONTON'}]
            w['tags']=[{'class':'generic','label':'Humano ONTON'}]
    if 'root-bal-2' in entries:
        words={w.get('id'):w for w in entries['root-bal-2'].get('words',[])}
        for wid in ('lexeme-dorbalo','lexeme-dorbalin'):
            w=words.get(wid)
            if w:
                suffix=' + <a class="morph-link" href="#morph-o">-O</a>' if wid=='lexeme-dorbalo' else ' + <a class="morph-link" href="#morph-in">-IN</a>'
                suffix_text=' + -O' if wid=='lexeme-dorbalo' else ' + -IN'
                suffix_ref={'id':'morph-o','label':'-O'} if wid=='lexeme-dorbalo' else {'id':'morph-in','label':'-IN'}
                w['analysis_html']='<a class="morph-link" href="#root-dors">DOR</a> (forma primigenia de *DOR-S) + BAL'+suffix
                w['analysis_text']='DOR (forma primigenia de *DOR-S) + BAL'+suffix_text
                w['refs']=[{'id':'root-dors','label':'DOR-S'},suffix_ref]
        w=words.get('lexeme-virbalcha')
        if w:
            w['analysis_html']='<a class="morph-link" href="#root-vir">VIR</a> + BAL + <a class="morph-link" href="#morph-cha-disease">-ĈA</a>'
            w['analysis_text']='VIR + BAL + -ĈA'
            w['refs']=[{'id':'root-vir','label':'VIR'},{'id':'morph-cha-disease','label':'-ĈA'}]
            w['tags']=[{'class':'generic','label':'Enfermedad ĈA'}]
    if 'root-bak' in entries:
        words={w.get('id'):w for w in entries['root-bak'].get('words',[])}
        w=words.get('lexeme-bakantan')
        if w:
            w['analysis_html']='BAK + <a class="morph-link" href="#morph-antan">-ANTAN</a>'
            w['analysis_text']='BAK + -ANTAN'
            w['refs']=[{'id':'morph-antan','label':'-ANTAN'}]
            w['tags']=[{'class':'generic','label':'Humano ANTAN'}]
        entries['root-bak']['notes']=[n for n in entries['root-bak'].get('notes',[]) if 'ANT de bakantan' not in n]
    bpath.write_text(json.dumps(bdata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    changed_paths.append('lexico/b.json')

    # A: arcantan comparte -ANTAN; -ONTAN de AŜV permanece distinto.
    apath=LEX/'a.json'
    adata=json.loads(apath.read_text(encoding='utf-8'))
    for e in adata.get('entries',[]):
        for w in e.get('words',[]):
            if w.get('id')=='lexeme-arcantan':
                w['analysis_html']='ARC-A + <a class="morph-link" href="#morph-antan">-ANTAN</a>'
                w['analysis_text']='ARC-A + -ANTAN'
                w['refs']=[{'id':'morph-antan','label':'-ANTAN'}]
                w['tags']=[{'class':'generic','label':'Humano ANTAN'}]
    apath.write_text(json.dumps(adata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    changed_paths.append('lexico/a.json')

    # D: la raíz se reanaliza como *DOR-S, con DOR- como forma primigenia.
    dpath=LEX/'d.json'
    ddata=json.loads(dpath.read_text(encoding='utf-8'))
    for e in ddata.get('entries',[]):
        if e.get('id')=='root-dors':
            e['form']='*DOR-S'
            e['gloss']='dorsal, espalda'
            e['notes']=['DOR- es la forma primigenia; DORS es la forma extendida usual. La forma primigenia aparece en derivados como dorbalo y dorbalin.']
    dpath.write_text(json.dumps(ddata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    changed_paths.append('lexico/d.json')

    # Gramática: documentar la relación estructural y distinguir -ONTON de -ONTAN.
    gpath=ROOT/'gramatica.html'
    g=gpath.read_text(encoding='utf-8')
    dor_para='  <p><span class="status canon">Canónico</span><code>*DOR-S</code> sigue el mismo patrón: <code>DOR-</code> es la forma primigenia de valor dorsal y <code>DORS</code> la forma extendida usual. La base primigenia aparece en derivados como <code>dorbalo</code> «giba, joroba» y <code>dorbalin</code> «jorobado».</p>\n'
    anchor='  <p><span class="status canon">Canónico</span>Así, <code>*OẐ-AN-</code> tiene como forma primigenia <code>OẐ-</code> y como forma extendida usual <code>OẐ-AN-</code>; <code>oẑastren</code> «estrella de mar» emplea la forma primigenia <code>OẐ-</code>. Del mismo modo, en raíces como <code>*AS-TR</code>, la parte posterior al guion es una extensión histórica de la raíz, aunque la forma extendida sea la de uso ordinario.</p>\n'
    if dor_para not in g and anchor in g:
        g=g.replace(anchor,anchor+dor_para)
    old='  <p><span class="status canon">Canónico</span>Dentro de la serie <code>-ONAS</code>, el participio se forma como <code>-ONAR</code> (<code>-ONAS → -ONAR</code>). Para designar «persona dedicada a» esa actividad se usa <code>-ONTAN</code>, en lugar del analógico esperado <code>*-ONISTAN</code>.</p>\n'
    new=old+'  <p><span class="status canon">Canónico</span><code>-ONTAN</code> y <code>-ONTON</code> son morfemas distintos. <code>-ONTAN</code> pertenece a la serie de <code>-ONAS</code>; <code>-ONTON</code> es una extensión parcialmente reduplicada del <code>-ON</code> humano. De modo paralelo, <code>-ANTAN</code> es una extensión parcialmente reduplicada del <code>-AN</code> humano agentivo.</p>\n'
    if '<code>-ONTAN</code> y <code>-ONTON</code> son morfemas distintos' not in g and old in g:
        g=g.replace(old,new)
    disease_row='    <tr><td><code>-ĈA</code></td><td><strong>enfermedad o afección</strong>; por ejemplo <code>virbalĉa</code> «balanitis»</td></tr>\n'
    row_anchor='    <tr><td><code>-AĈ-</code></td><td>intensificativo verbal</td></tr>\n'
    if disease_row not in g and row_anchor in g:
        g=g.replace(row_anchor,disease_row+row_anchor)
    human_rows='    <tr><td><code>-ONTON</code></td><td>extensión parcialmente reduplicada del <code>-ON</code> humano</td></tr>\n    <tr><td><code>-ANTAN</code></td><td>extensión parcialmente reduplicada del <code>-AN</code> humano agentivo</td></tr>\n'
    human_anchor='    <tr><td><code>-AN</code></td><td>humanos agentivos</td></tr>\n'
    if '<code>-ONTON</code></td>' not in g and human_anchor in g:
        g=g.replace(human_anchor,human_anchor+human_rows)
    gpath.write_text(g,encoding='utf-8')
    changed_paths.append('gramatica.html')

    subprocess.run(['git','add',*changed_paths],cwd=ROOT,check=True)

canonicalize_new_morphology()

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
