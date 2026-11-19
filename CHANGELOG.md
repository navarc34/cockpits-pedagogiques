# Historique des versions

Les versions de l'application suivent SemVer et utilisent le suffixe `-beta.N` avant la première version stable. Les synchronisations de données ne modifient pas automatiquement le numéro de version applicative.

## 0.2.0-beta.2 — 20 novembre 2026
- Journal de bord dans chaque cours : bilans de séance restitués en trois rubriques (ce qui a marché / à améliorer / pistes et idées), items datés et préfixés du titre de la séance Pronote correspondante.
- Marqueur « URGENT » des bilans : extraction automatique vers les priorités court et moyen terme, badge rouge « ⚑ URGENT » en tête de la liste « À venir ».
- Priorités court terme : échéances ISO comparables (`dateEcheance`), tri par échéance, badge « dépassée » pour les retards réels, alerte « à saisir Pronote » calculée dynamiquement depuis les séances.
- Collecte automatisée consolidation des sources Drive (exports Pronote, dossiers H{n}, bilans) deux fois par jour, orchestrée par un skill unique ; maintenance des topics Knowledge de suivi à chaque exécution.
- Fiabilité des collections : protection des gros fichiers JSON (lecture intégrale par tranches avant push), garde de confidentialité et de cohérence systématique avant publication, contrats de versionnage entre `release.json` et les scénarios pédagogiques.
- Historique des versions : page dédiée `changelog.html` avec encodage UTF-8 explicite (fin des caractères mal affichés), ouverture dans un nouvel onglet depuis le pied de page.

## 0.2.0-beta.1 — 14 novembre 2026
- Première version bêta explicitement identifiée dans les trois pages.
- Séparation version de l'application / révision des données / statut des trajectoires.
- Suppression du simulateur de transfert d'heures jugé non utile ; maintien de la vue du cap et des allocations proposées.
- Préparation d'un registre de scénarios pédagogiques pour le latin option et spécialité, sans plan annuel fictif.
- Contrats de validation pour les métadonnées de version et de scénarios.

## Avant versionnement
- Création des cockpits (référence `dev-claude`).
- Sprints 1A–1D sur `dev-chatgpt` : objectifs, sources, calendrier prévisionnel, preuves, modèle de trajectoire.
