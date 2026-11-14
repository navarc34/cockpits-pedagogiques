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

## Sprint 1C — Séances candidates et vérification pédagogique

- `data/pilotage.json` v3 déclare pour chaque objectif une règle `reconnaissance` (`regex` sur des champs explicités ou `manuel`).
- `assets/trajectoire-evidence.js` produit des correspondances *candidates* uniquement pour les séances documentées au plus tard à la date d'arrêté ; les séances futures et les entrées « à saisir » ne sont pas des preuves.
- L’interface affiche les séances candidates avec date, titre, statut, champs correspondants, référence stable dérivée de date + heure et motif de reconnaissance.
- Une même EL peut apparaître sur plusieurs séances : le nombre de correspondances **n'est pas** le nombre d'EL validées.
- Les exclusions et confirmations déclarées dans `realisation` prévalent sur la règle automatique. Leur validation reste un acte humain et doit être saisie dans le JSON versionné.
- `tests/test_preuves.cjs` protège le cutoff, la non-duplication, le fonctionnement des exclusions, le mode manuel et les regex invalides ; `tests/test_pilotage.py` vérifie la structure des règles.
- Limite : une clé de séance `date+heure` peut entrer en collision pour des créneaux simultanés ou changer après déplacement. Pour une généralisation, prévoir de vrais IDs persistants dans les exports.

## Sprint 1D — Cap annuel, projection et scénarios

- `data/trajectoire.json` : plan de travail **brouillon**, entièrement illustratif. Les allocations totalisent les 74 heures du budget arrêté au 13 novembre, mais ne représentent pas un plan approuvé.
- Six enveloppes : Graffigny, Rimbaud, Chrétien de Troyes, Musset, exercices transversaux et réserve. Leurs fenêtres sont des hypothèses de répartition, à confronter aux séquences et à l'emploi du temps.
- `assets/trajectoire-projection.js` : vérification des invariants (budget total et arrêté), projection des capacités théoriques des fenêtres et simulations sans mutation ni persistance.
- La capacité reconstruite à partir des récurrences peut différer du solde issu de l'agenda. Cette divergence est à vérifier et n'est **jamais** une preuve de retard.
- `trajectoire.html` : le cap annuel est maintenant placé en haut. Le sélecteur de bloc et le curseur simulent une variation d'heures financée ou non par la réserve. Aucun scénario n'est écrit dans les JSON.
- `schemas/trajectoire.schema.json`, `tests/test_trajectoire.py` et `tests/test_projection.cjs` valident budget, dates, doublons, calculs et immutabilité ; la CI exécute les tests.
- Le passage d'un plan brouillon à un plan validé et son historique doivent résulter d'une décision explicite de l'enseignant et d'une nouvelle version des données.

## Bêta et versionnement
La simulation de réallocation d'heures a été retirée après recette. Le cap et les budgets proposés restent visibles. La version applicative, la révision de données et le statut des progressions sont séparés dans `data/release.json`. Les propositions de progression latin vivront dans `data/progression-scenarios.json` sans devenir un cap validé tant qu'une décision explicite n'est pas enregistrée.
