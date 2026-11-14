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

## Sprint 1B — Calendrier prévisionnel et comparaison exploratoire

- Modèle de récurrence français : lundi 11 h, vendredi 10 h ; troisième heure alternée entre vendredi 13 h et lundi 15 h, avec ancrage au lundi 7 septembre 2026.
- Cette règle est une **hypothèse déduite des séances**, pas un emploi du temps certifié. Les jours fériés et les exceptions non encore vérifiés imposent ce statut.
- Les vacances utilisent une borne de fin exclusive (date de reprise). Cela permet de conserver la séance renseignée le 2 novembre.
- Les heures théoriques, séances documentées comme publiées/distancielles et créneaux sans confirmation sont affichés séparément.
- Une séance à saisir ou manquante n'est pas qualifiée de non réalisée. Les statuts postérieurs à la date d'arrêté ne constituent pas un fait acquis.
- Fenêtre Rimbaud (23 novembre au 18 décembre) : estimation exploratoire, à rapprocher de l'agenda.
- Tests automatisés : modèle Python et moteur JavaScript Node, exécutés dans la CI.
