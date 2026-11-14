# Cockpits pédagogiques — 2026-2027

Pilotage de trois cours : priorités court / moyen / long terme, budget d'heures, calendrier, historique Pronote, progression, programme, grammaire, culture.

## Architecture
- `index.html` — cockpit général · `cours.html?id=fr|option|spe` — cockpit d'un cours (onglets, détail des séances en accordéon).
- `data/*.json` — source de vérité, lue par `fetch()` ; les pages ne changent pas pour une mise à jour de contenu. Tout est statique, sans build.
- `data/*.json › meta.arrete` : date d'arrêté des comptes. `budget.consomme` doit égaler la somme des heures des séances jusqu'à cette date (vérifié par `validate.py`).
- `archive/v1/` — ancien chantier (non utilisé par les pages).

## Développement local
`python3 -m http.server 5500`, puis http://127.0.0.1:5500 (le `file://` ne fonctionne pas : `fetch` est bloqué). `?now=AAAA-MM-JJ` simule une autre date du jour.

## Sécurité et confidentialité
Le dépôt est public : aucune donnée nominative (personnes, établissement, classes, liens privés) dans `data/`.
- Activer la garde locale : `git config core.hooksPath scripts/hooks` (lance `check_privacy.py` et `validate.py` avant chaque push).
- La CI rejoue les deux scripts, mais elle s'exécute **après** le push : le hook est la vraie barrière.
- Les termes interdits sont stockés sous forme d'empreintes (`scripts/privacy_hashes.txt`). Ajouter un terme : `python3 scripts/check_privacy.py --hash MOT`. Liste en clair facultative et ignorée par git : `scripts/privacy_local.txt`.
- Les pages portent `noindex` : cela limite l'indexation, ce n'est pas un contrôle d'accès.
