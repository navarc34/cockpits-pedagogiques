#!/usr/bin/env python3
"""Garde de confidentialité — à lancer avant tout push (hook pre-push) et en CI.

Aucun terme sensible n'est écrit en clair dans le dépôt : les mots interdits sont
stockés sous forme d'empreintes SHA-256 (scripts/privacy_hashes.txt). Les messages
d'erreur masquent le terme trouvé (les journaux d'une CI publique sont publics).

  python scripts/check_privacy.py                 # contrôle tout l'arbre
  python scripts/check_privacy.py --hash MOT      # empreinte à ajouter à privacy_hashes.txt
Liste locale facultative en clair (ignorée par git) : scripts/privacy_local.txt
"""
import hashlib, pathlib, re, sys, unicodedata
R = pathlib.Path(__file__).resolve().parent.parent
SKIP = {'.git', 'node_modules'}
EXT = {'.html', '.json', '.md', '.py', '.yml', '.yaml', '.txt', '.js', '.css', '.svg', '.code-workspace', '.gitignore', '.gitattributes', ''}
norm = lambda s: ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
sha = lambda w: hashlib.sha256(norm(w).encode()).hexdigest()
if len(sys.argv) == 3 and sys.argv[1] == '--hash':
    print(sha(sys.argv[2])); sys.exit(0)
H = {l.split('#')[0].strip() for l in (R/'scripts/privacy_hashes.txt').read_text().splitlines()} - {''}
loc = R/'scripts/privacy_local.txt'
if loc.exists(): H |= {sha(w) for w in loc.read_text(encoding='utf-8').split()}
PAT = [(r'[\w.+-]+@[a-z0-9-]+\.[a-z]{2,}', 'adresse e-mail'),
       (r'(?<!\d)0[1-9](?:[ .]?\d{2}){4}(?!\d)', 'numéro de téléphone'),
       (r'cv-aura|digipad\.app|chat\.mistral|drive\.google|docs\.google|zoom\.us|meet\.google|teams\.microsoft', 'lien privé'),
       (r'\bst2s\s?\d\b', 'code de classe')]
mask = lambda w: w[0] + '*' * (len(w) - 1)
bad = []
for p in sorted(R.rglob('*')):
    rel = p.relative_to(R)
    if not p.is_file() or SKIP & set(rel.parts) or p.suffix.lower() not in EXT or rel.as_posix() == 'scripts/privacy_hashes.txt' or p == loc or rel.as_posix() == 'scripts/check_privacy.py': continue
    for t in re.findall(r'[a-z0-9]+', norm(rel.as_posix())):
        if sha(t) in H: bad.append(f'{rel} : mot interdit dans le NOM du fichier ({mask(t)})')
    try: lines = p.read_text(encoding='utf-8').splitlines()
    except UnicodeDecodeError: continue
    for i, line in enumerate(lines, 1):
        for t in set(re.findall(r'[a-z0-9]+', norm(line))):
            if sha(t) in H: bad.append(f'{rel}:{i} : mot interdit ({mask(t)})')
        for rx, kind in PAT:
            if re.search(rx, line, re.I): bad.append(f'{rel}:{i} : {kind}')
if bad:
    print('CONFIDENTIALITÉ — push à bloquer :'); print('\n'.join(bad[:40])); sys.exit(1)
print('confidentialité : OK')
