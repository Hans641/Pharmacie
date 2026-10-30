# État du développement

Dernière vérification : **30 octobre 2026**. Reprise de recette à `main` / `7c871d3` ; référence locale `origin/main` identique lors de l’inspection. Cela ne prouve pas à lui seul l’état distant en temps réel.

## Fonctions implémentées et preuves disponibles

| Ensemble | Preuves | Limites |
|---|---|---|
| Auth, rôles, comptes, CSRF, accès | vues/formulaires/setup_roles ; InterfaceTests et tests de permissions | SMTP réel et protection anti-bruteforce non validés |
| Catalogue, catégories, fournisseurs, clients, photos et archivage | modèles/forms/entity_* ; tests images, recherche, historique et accès | Pas de recette utilisateur complète attestée |
| Achats et réceptions partielles | services et tests reliquat, rollback, réception unique | Écran de réception par ligne ; service accepte plusieurs lignes |
| Lots, FEFO, inventaire et mouvements | services, BusinessTests | PostgreSQL et forte charge non testés |
| Vente, paiement intégral, ordonnance, concurrence | tests atomicité, stock, historique, double validation et concurrence | Électronique manuel ; pas de réservation globale des brouillons |
| Retours et remise en stock contrôlée | tests quantité, idempotence, lot périmé et historique | Remboursement exécuté hors logiciel |
| Dashboard et PDF | code de calcul, tests de rendu et signature PDF | Rendu visuel PDF/ReportLab et conformité fiscale non établis |
| Sauvegarde/restauration SQLite | BackupTests | Test isolé ; pas de reprise de production attestée |
| Design system, composants, navigation et formulaires progressifs | templates/static, PresentationTests et ProgressiveFormTests | WCAG AA et quatre largeurs non certifiées |
| Prévisualisations réception/inventaire/retour | OperationPresentationTests, 9 tests JS | Estimations ; validation métier serveur |
| Caisse améliorée | CashierExperienceTests, 12 tests JS ; fusion c3026db | Temps de vente <30 s et usage matériel non mesurés |

## Vérifications de la session documentaire précédente

Environnement : Python 3.12.3, Django 6.0.4, ReportLab absent.

- `.venv/bin/python manage.py test --verbosity 1` : **79 tests réussis**, 158,296 s ; base de test créée puis détruite.
- `.venv/bin/python manage.py check` : aucune anomalie signalée.
- `.venv/bin/python manage.py makemigrations --check --dry-run` : aucun changement détecté ; aucune migration créée ou appliquée.
- `node tools/cashier_math.test.mjs` : **12 réussis**.
- `node tools/operation_math.test.mjs` : **9 réussis**.

Les tests PDF vérifient notamment réponse, type et signature ; ils ne prouvent pas la lisibilité des documents. Les tests de concurrence SQLite acceptent des refus temporaires et contrôlent l’absence de double sortie/stock négatif ; ils ne constituent pas un test de charge ni une preuve de verrouillage de ligne.

## Dernière étape et travail actuel

Caisse, dashboard et stocks sont intégrés ; fusion stocks confirmée à `7c871d3` dans le dépôt actif. La référence locale `origin/main` est identique lors de la reprise ; le push a été déclaré effectué par l'utilisateur, sans vérification distante depuis l'agent. Tâche actuelle réorientée par l'utilisateur : mode sombre commun à toutes les pages, avec préférence système et choix explicite en pied de page. La recette navigateur reste incomplète ; le dernier rapport `6zmmb904` échoue sur un clic de période instable, sans preuve de résolution. Aucun commit, merge ou push demandé pour cette étape.

## Prochaines étapes prioritaires

1. Recette réelle de caisse sur données isolées, aux largeurs 360, 768, 1280 et 1920 px : clavier, focus, mobile, erreurs, paiement, ordonnance, impression et absence de double soumission. Suivre `../RECETTE_CAISSE.md` et `../RECETTE_UX.md` ; documenter les résultats plutôt que supposer la réussite.
2. Mesurer plusieurs ventes fictives représentatives et vérifier l’objectif de 30 secondes.
3. Après la recette du dashboard clarifié, poursuivre les stocks/listes, après inspection des améliorations déjà présentes. Comparer au plan `../AUDIT_UX.md` et ne pas refaire les composants existants.
4. Avant exploitation : SMTP, HTTPS/serveur WSGI, protection des tentatives de connexion, supervision, sauvegardes hors machine, validation locale des documents/procédures ; voir `../EXPLOITATION.md`.

## Non réalisé ou incertain

Pas de multi-tenant, SaaS rizicole, paiement partiel, intégration prestataire, comptabilité générale, prescription automatique, mode hors ligne complet ou scanner caméra. Pas de validation navigateur complète, de conformité WCAG 2.2 AA attestée, de certification fiscale ni de déploiement de production démontré. Le fonctionnement des ressources locales n’implique pas une application hors ligne.

## Itération UI — tableau de bord, 30 octobre 2026

- Situation actuelle et période analysée distinguées ; filtres datés explicites, retour au mois en cours, liens de section et limites des aperçus.
- Aucun changement de vue, calcul, permission, modèle ou migration. Recette navigateur aux quatre largeurs encore à exécuter.
- Vérification ciblée : résultats consignés dans SESSION_LOG ; les 79 tests ci-dessus concernent la session documentaire précédente.

## Recette et intégration — 30 octobre 2026

- `DashboardPeriodTests` ajoute trois tests : distinction période/données actuelles, dates inversées, affichage pour les cinq rôles et sans permissions. Le gestionnaire de stock conserve le filtre des achats sans voir les chiffres des ventes.
- Le script navigateur couvre maintenant les ancres au clavier, la période passée, le retour au mois courant et les filtres sans JavaScript. Exécution complète non réalisée : Chrome échoue avant rendu avec `setsockopt: Operation not permitted` ; Playwright Node n'est pas installé dans le projet.
- Les 21 tests JS restent réussis ; syntaxe du script navigateur, check Django et absence de changement de migration vérifiés.
- Intégration préparée sur `feat/dashboard-clarity` dans une copie isolée, avec fusion sans fast-forward. Le bundle et le finaliseur sous `.publication/` sont locaux et ignorés. Ils ne signifient pas que le dépôt actif ou GitHub a été modifié. Référence du dépôt actif lors de la préparation : `c3026db`.

Validation finale de cette itération : **82 tests Django réussis en 153,801 s**, **21 tests JS réussis**, `manage.py check` sans anomalie, `makemigrations --check --dry-run` sans changement, `node --check tools/ux_browser_check.cjs` et `git diff --check` réussis. Recette navigateur non validée pour les raisons ci-dessus.

## Stocks et lots — 30 octobre 2026

- Libellés visibles, filtres rapides conservant la recherche et retirant la page, compte filtré et tri explicite. Aide native sur stock physique, disponibilité et cumul des états.
- Lots épuisés et lots bloqués/périmés explicités ; liens médicament et inventaire soumis aux permissions. États vides avec action de réinitialisation.
- Fichiers et recette : `../RECETTE_STOCKS.md`. Aucun tri global supplémentaire ni persistance hors URL ajouté. Recette navigateur aux quatre largeurs toujours à réaliser.

Vérification stocks : **15 tests ciblés réussis (28,454 s)**, check Django et `git diff --check` sans erreur. La suite complète de 82 tests mentionnée plus haut concerne l'itération dashboard ; trois tests stocks s'y ajoutent, sans nouveau passage complet attesté.

## Recette responsive/clavier — 30 octobre 2026

- Nouveau lanceur `tools/run_ux_review.py` : cinq rôles, base/médias temporaires, port libre, mot de passe non persistant, rapports conservés ; mode `--prepare-only` sans socket ni navigateur. Documentation dans `../RECETTE_UX.md`.
- Préparation vérifiée : 45 rendus serveur, DATABASE_PATH hérité ignoré, sentinelle et empreintes base active/médias inchangées.
- Script navigateur complété : évitement au clavier, boucle Tab/Maj+Tab du tiroir, captures du menu, captures et débordements sans JS aux quatre largeurs, rapport/capture sur échec après lancement.
- Blocages réellement confirmés : Chrome échoue avant rendu ; le lancement complet échoue également à l'ouverture du serveur local. Aucune réussite visuelle/clavier navigateur revendiquée. Prochaine action : exécuter `.venv/bin/python tools/run_ux_review.py` depuis le terminal hôte, puis examiner résultats et captures et corriger les défauts constatés.

Contrôles de cette session : **85 tests Django réussis (158,444 s)**, **21 tests JS réussis**, check Django, compilation Python, syntaxe du script navigateur et diff sans erreur. Cela ne valide pas les nouvelles assertions Playwright ; exécution sur l'hôte encore nécessaire.

## Premier retour navigateur hôte — 30 octobre 2026

Rapport `sn78_rcg` : 11 pages administrateur à 360 px et dashboard à 768 px passent avec JS ; échec catalogue à 768 px. Capture inspectée : colonnes comprimées et mots morcelés. Faux positifs également constatés sur les liens de menus fermés. CSS du catalogue/cartes et mesure des éléments visibles corrigés ; premier menu ouvert désormais contrôlé. Nouvelle recette hôte attendue ; autres rôles, largeurs et sans JS non validés par ce passage.

### Retour hôte z_0k5lok — 30 octobre 2026

Le catalogue à 768 px passe après correction ; 20 parcours de page avec JS sont enregistrés comme réussis pour l'administrateur (11 à 360 px, neuf à 768 px). Arrêt sur la création de médicament : le scénario attend le champ prix alors que la capture montre toujours Identification. Cause exacte du non-avancement non démontrée. Le scénario active maintenant Continuer au clavier et vérifie l'étape atteinte, avec restitution des messages inline si elle reste bloquée. Aucun changement de validation applicative. Syntaxe Node et diff vérifiés ; nouvelle exécution hôte requise, les autres rôles et le sans-JS restent non validés.

## Mode sombre — 30 octobre 2026

- Thème commun clair/sombre : tokens, surfaces, tableaux, formulaires, états, navigation, caisse, progression, notifications et connexion. Sélecteur Système/Clair/Sombre sur toutes les pages de base ; préférence locale non sensible et synchronisation des onglets. Sans JS : préférence système.
- Couverture et recette : `../MODE_SOMBRE.md`. Impression claire maintenue, PDF indépendants. Aucun changement métier ou de permission.
- Vérification : 12 tests ciblés réussis (22,704 s), check Django, syntaxe JS et diff sans erreur. 17 paires de texte par palette calculées >=4,5:1 ; focus/bordures de champs >=3:1 sur surface. Préférence, stockage et synchronisation vérifiés en VM Node. Ces contrôles ne prouvent pas le rendu navigateur du mode sombre.
- Prochaine vérification : sélectionner Sombre en pied de page et examiner les familles de pages aux quatre largeurs, puis l'aperçu d'impression. Recette générale et objectif caisse de 30 secondes toujours non validés.
