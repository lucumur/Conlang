"""Valida la integridad del léxico. Sale con código 1 si encuentra errores.

Comprueba:
  - que cada lexico/*.json sea JSON válido;
  - que no haya ids duplicados entre raíces, vocablos y morfemas;
  - que cada raíz esté en el archivo de su letra;
  - que cada referencia (refs y enlaces morph-link del análisis) apunte a un id existente;
  - que index.json coincida con lo que generaría scripts/build_lexicon_index.py.
"""
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
import shutil

ROOT = Path(__file__).resolve().parents[1]
LEX = ROOT / 'lexico'
errors = []


def load(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:  # JSON roto
        errors.append(f'{path.relative_to(ROOT)}: JSON inválido ({exc})')
        return None


files = {p.name: load(p) for p in sorted(LEX.glob('*.json'))}
if errors:
    print('\n'.join(errors))
    sys.exit(1)

LETTER_FILES = [
    ('A','a'),('B','b'),('C','c'),('Ĉ','circ-c'),('D','d'),('E','e'),('F','f'),('G','g'),('Ĝ','circ-g'),
    ('I','i'),('J','j'),('Ĵ','circ-j'),('K','k'),('L','l'),('M','m'),('N','n'),('O','o'),('P','p'),('R','r'),('S','s'),
    ('Ŝ','circ-s'),('T','t'),('Θ','theta'),('U','u'),('V','v'),('Z','z'),('Ẑ','circ-z')
]

ids = {}
def claim(i, where):
    if not i:
        errors.append(f'{where}: entrada sin id')
    elif i in ids:
        errors.append(f'id duplicado «{i}»: {ids[i]} y {where}')
    else:
        ids[i] = where

words = []
for letter, key in LETTER_FILES:
    name = f'{key}.json'
    data = files.get(name)
    if data is None:
        errors.append(f'falta lexico/{name}')
        continue
    for e in data.get('entries', []):
        claim(e.get('id'), f'{name} raíz {e.get("form")}')
        for w in e.get('words', []) or []:
            claim(w.get('id'), f'{name} vocablo {w.get("form")}')
            words.append((name, w))

for m in files['morphemes.json'].get('morphemes', []):
    claim(m.get('id'), f'morphemes.json morfema {m.get("form")}')

href = re.compile(r'href="#([^"]+)"')
for name, w in words:
    targets = [r.get('id') for r in w.get('refs', []) or [] if r.get('id')]
    targets += href.findall(w.get('analysis_html', '') or '')
    for t in dict.fromkeys(targets):
        if t not in ids:
            errors.append(f'{name} vocablo {w.get("form")}: referencia a «{t}», que no existe')

word_ids = {w.get('id') for _, w in words}
for name, w in words:
    for p in w.get('proviene_de', []) or []:
        pid = p.get('id')
        if pid == w.get('id'):
            errors.append(f'{name} vocablo {w.get("form")}: proviene de sí mismo')
        elif pid not in word_ids:
            errors.append(f'{name} vocablo {w.get("form")}: proviene_de «{pid}», que no es un vocablo existente')
    if 'paradigma' in w:
        where = f'{name} vocablo {w.get("form")}'
        p = w['paradigma']
        if not isinstance(p, dict):
            errors.append(f'{where}: paradigma no es un objeto')
        else:
            extra = set(p) - {'tipo', 'titulo', 'nota', 'filas'}
            if extra:
                errors.append(f'{where}: paradigma tiene campos no previstos: {", ".join(sorted(extra))}')
            if p.get('tipo') not in ('conjugacion', 'declinacion'):
                errors.append(f'{where}: paradigma.tipo debe ser conjugacion o declinacion')
            filas = p.get('filas')
            ok = isinstance(filas, list) and filas and all(isinstance(r, list) and r and all(isinstance(c, str) for c in r) for r in filas)
            if not ok:
                errors.append(f'{where}: paradigma.filas debe ser una tabla rectangular de textos')
            else:
                width = len(filas[0])
                if any(len(r) != width for r in filas):
                    errors.append(f'{where}: paradigma con filas de distinto ancho')
                if not any(c for r in filas for c in r):
                    errors.append(f'{where}: paradigma vacío; omite el campo')
            for key in ('titulo', 'nota'):
                if key in p and (not isinstance(p[key], str) or not p[key]):
                    errors.append(f'{where}: paradigma.{key} debe ser texto no vacío, u omitirse')

# index.json debe ser idéntico al que genera el script oficial
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    shutil.copytree(LEX, tmp / 'lexico')
    (tmp / 'scripts').mkdir()
    shutil.copy(ROOT / 'scripts' / 'build_lexicon_index.py', tmp / 'scripts')
    subprocess.run([sys.executable, str(tmp / 'scripts' / 'build_lexicon_index.py')], check=True, capture_output=True)
    if json.loads((tmp / 'lexico' / 'index.json').read_text(encoding='utf-8')) != files['index.json']:
        errors.append('index.json no coincide con lo que genera build_lexicon_index.py')

if errors:
    print(f'{len(errors)} problema(s) en el léxico:')
    print('\n'.join('  - ' + e for e in errors))
    sys.exit(1)
print(f'Léxico válido: {len(ids)} ids, {len(words)} vocablos.')
