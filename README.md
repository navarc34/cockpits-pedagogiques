# Cockpits pédagogiques — v2

Cockpit prof : pilotage des 3 cours (Français 1ère ST2S · Option latin LCA · Spécialité LLCA latin), année 2026-2027.

## Architecture (v2)

- **`index.html`** — cockpit général : accès aux 3 cockpits de cours, priorités court / moyen / long terme (tous cours), budget d'heures (total / consommé / à venir), calendrier des dates importantes (vacances, conseils de classe, réunions parents-prof, échéances, événements type élection présidentielle).
- **`cours.html?id=fr|option|spe`** — page de synthèse par cours (tableau de bord) + rubriques : priorités · Pronote détaillé (scroll vertical, vue résumée puis détail au clic) · timeline annuelle (scroll horizontal) · progression annuelle (établie ou en chantier, avec pistes) · éléments du programme vus / pas vus · grammaire vus / à voir · auteurs, textes, références culturelles, périodes.
- **`data/*.json`** — source de vérité structurée, versionnée dans ce dépôt. L'IA ne pousse que du JSON ; les pages le lisent par `fetch`.

## Données (`data/`)

- `global.json` — priorités globales, budgets d'heures (agenda Google), calendrier.
- `fr.json`, `option.json`, `spe.json` — par cours : séances (parsing des exports Pronote du 12/11/2026), jalons, progression, couverture du référentiel Pronote, grammaire, culture.

Mise à jour : remplacer l'export Pronote parsé dans `data/{cours}.json` (clé `seances`) et recroiser la clé `programme` avec le référentiel.

## Sources

- Exports Pronote du 12/11/2026 (dossiers `____EDT_EXPORTS_PRONOTE` de chaque cours).
- Créneaux de cours comptés dans l'agenda Google (base du budget d'heures).
- Progressions annuelles / cadres de travail (Drive + Knowledge).
