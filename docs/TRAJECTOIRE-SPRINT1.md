# Trajectoire pédagogique — Sprint 1A

La page `trajectoire.html` (français uniquement) reste **en lecture seule**. Les objectifs sont proposés et leur validation appartient au professeur.

- `data/pilotage.json` v2 est la source structurée de cibles (maximum six objectifs pour le français) et d'actions déclarées.
- `schemas/pilotage.schema.json` décrit les types, champs obligatoires et valeurs permises ; `tests/test_pilotage.py` vérifie le schéma et les références (y compris des cas de rejet), exécuté en CI.
- `data/fr.json` comporte des IDs stables sur les jalons référencés par les actions ; le texte de ces jalons n'est plus une clé de liaison.
- `realisation.confirmees`, `candidates`, `exclues` distinguent une preuve validée, une suggestion et une exclusion ; toutes les listes sont vides au lancement. **Aucune maîtrise des élèves n'est déduite automatiquement**.
- Les dates consultées avant `meta.dateReference` ne sont pas présentées comme une reconstitution historique : l'interface demande de véritables instantanés.
- Pour les dates après `meta.arrete`, les budgets sont explicitement marqués comme arrêtés ; les événements ultérieurs ne sont pas comptés comme effectués.
- L'interface conserve des décisions *à instruire* ; une échéance dépassée n'est pas une preuve de non-réalisation.
- Le calcul précis du prévu/réalisé est reporté : le calendrier de récurrence Q1/Q2, vacances et exceptions doit d'abord être confirmé, sans valeur fictive.

## Recette
Servir le dépôt via HTTP, ouvrir `trajectoire.html?now=2026-11-14`, puis tester `?now=2026-11-01` (historique non reconstructible) et `?now=2026-11-30` (données périmées). Vérifier les liens vers la timeline, le mode sombre, le clavier et le mobile. Ne pas fusionner sans validation.
