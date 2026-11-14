# Versionnement et évolution continue — bêta

## Trois registres indépendants
1. **Application** — `data/release.json > application.version` : version SemVer, par exemple `0.2.0-beta.1`. Changement uniquement lorsqu'un ensemble de modifications de code/interface est publié. Historique humain dans `CHANGELOG.md`.
2. **Données** — `data/release.json > data.revision` : révision de l'instantané public anonymisé, distincte du code ; `data.arrete` est la date de référence des données. `lastSuccessfulSync: null` signifie qu'aucun pipeline de collecte n'est attesté.
3. **Trajectoires** — statuts `brouillon`, `en construction` ou `validée`, distincts du fait qu'un fichier ait été actualisé. Un changement de scénario n'est pas une validation pédagogique.

## Latin option et spécialité
`data/progression-scenarios.json` sert de registre d'options de progression. Les deux cours de latin sont **en construction**. Des propositions futures, fondées sur des documents Hn, ressources et instructions du professeur, peuvent y être déposées en tant que brouillons sans modifier l'organisation des pages `cours.html`. L'architecture générique doit rester stable.

## Collecte automatique future (non activée)
Une tâche pourra se déclencher plusieurs fois par jour. Elle devra : consulter les sources privées autorisées dans Drive ; construire un instantané **anonymisé** ; comparer avec le dernier instantané validé ; exécuter les contrôles de schéma, cohérence et confidentialité **avant tout push public** ; publier atomiquement une nouvelle révision de données ; conserver la provenance et consigner les divergences ou erreurs.
Une collecte sans changement de données n'incrémente pas la révision ; une collecte échouée ne modifie pas la date de synchronisation réussie. L'absence de nouvelle séance n'est jamais interprétée automatiquement comme un cours non assuré. Les données privées ne doivent pas être copiées dans GitHub, y compris dans l'historique.

## Validation des décisions
Une progression proposée par une IA demeure au statut de proposition tant qu'elle n'a pas été explicitement validée. Les trajets d'apprentissage, les objectifs obligatoires et le programme ne changent pas automatiquement sous l'effet d'un export Pronote.
