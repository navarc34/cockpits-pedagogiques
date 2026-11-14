#!/usr/bin/env python3
"""Validation des données v2 et de la syntaxe JS des pages (sans dépendance Python)."""
import json, pathlib, re, shutil, subprocess, sys, tempfile
R = pathlib.Path(__file__).resolve().parent.parent
E = []; ISO = re.compile(r'^\d{4}-\d{2}-\d{2}$')
STAT = {'publié', 'réalisé non publié', 'distanciel', 'à saisir'}
def load(n):
    try: return json.loads((R/'data'/f'{n}.json').read_text(encoding='utf-8'))
    except Exception as e: E.append(f'{n}.json illisible : {e}')
g = load('global'); C = {k: load(k) for k in ('fr', 'option', 'spe')}
if g:
    for k in ('meta', 'courses', 'prioritesGlobales', 'calendrier'):
        if k not in g: E.append(f'global.json : clé « {k} » absente')
    if not ISO.match(str(g.get('meta', {}).get('arrete', ''))): E.append('global.json : meta.arrete (AAAA-MM-JJ) manquant')
    for e in g.get('calendrier', []):
        for f in ('date', 'fin'):
            if e.get(f) and not ISO.match(e[f]): E.append(f'calendrier : date invalide {e[f]}')
    for c in g.get('courses', []):
        d = C.get(c['id'])
        if not d: E.append(f"cours {c['id']} sans fichier"); continue
        if c['budget'] != d['budget']: E.append(f"budget global ≠ budget de {c['id']}.json")
        if not re.fullmatch(r'cours\.html\?id=\w+', c['href']): E.append(f"href invalide : {c['href']}")
for k, d in C.items():
    if not d: continue
    miss = [x for x in ('meta', 'budget', 'priorites', 'jalons', 'vacances', 'seances', 'programme', 'grammaire', 'culture', 'progression') if x not in d]
    if miss: E.append(f'{k}.json : clés absentes {miss}'); continue
    b = d['budget']
    if b['consomme'] + b['aVenir'] != b['total']: E.append(f'{k} : consommé + à venir ≠ total')
    a = d['meta'].get('arrete')
    if not (a and ISO.match(a)): E.append(f'{k} : meta.arrete manquant'); continue
    if g and a != g['meta'].get('arrete'): E.append(f'{k} : meta.arrete ≠ global')
    h = sum(s['hours'] for s in d['seances'] if s['date'] <= a)
    if h != b['consomme']: E.append(f"{k} : consommé = {b['consomme']} h, mais les séances jusqu'au {a} totalisent {h} h")
    for s in d['seances']:
        if not ISO.match(s['date']): E.append(f"{k} : date de séance invalide {s['date']}")
        if s['statut'] not in STAT: E.append(f"{k} : statut inconnu « {s['statut']} » ({s['date']})")
    for j in d['jalons']:
        if not ISO.match(j['date']): E.append(f"{k} : jalon à date invalide {j['date']}")
node = shutil.which('node')
for page in ('index.html', 'cours.html', 'trajectoire.html'):
    for js in re.findall(r'<script>(.*?)</script>', (R/page).read_text(encoding='utf-8'), re.S):
        if not node: print(f'avertissement : node absent, syntaxe JS de {page} non vérifiée'); break
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as t: t.write(js)
        r = subprocess.run([node, '--check', t.name], capture_output=True, text=True)
        if r.returncode: E.append(f'{page} : erreur de syntaxe JS — {r.stderr[:300]}')
if E: print('VALIDATION — erreurs :'); print('\n'.join('  ' + e for e in E)); sys.exit(1)
print('validation : OK')
