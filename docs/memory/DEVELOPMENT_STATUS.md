# État du développement

Dernière reprise vérifiée : **2 novembre 2026**. Dépôt propre au début de la reprise à `main` / `3b28d08`, fusion QA frontend ; référence locale `origin/main` identique. Pas d’interrogation distante. Les anciens états Git ci-dessous sont historiques.

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

La fusion `fix/recette-frontend` est confirmée à `3b28d08` (commits `9b2526e`, `f0fb6b7`, `ffed724`). La référence locale `origin/main` correspond ; aucun push effectué par l’agent.

Lot 1 : clic de période validé 20/20 ; lot 2 : 720 cas automatiques réussis et 144 cas stock après retouche. Lot 3 en cours : inspection de trois captures supplémentaires et préparation des mesures DOM/print via `--matrix --presentation`. Nouvelle exécution bloquée avant serveur : rapport `fkt1jp4z`, zéro requête. Résultats navigateur supplémentaires **non exécutés** ; commandes et limites dans `../RECETTE_PRESENTATION.md`. Aucun composant ni logique métier modifié pour cette reprise.

## Prochaines étapes prioritaires

1. Exécuter `--matrix --presentation --role administrateur`, examiner les contrastes et documents HTML imprimés ; poursuivre les autres rôles et les contrôles manuels (états, authentification/erreurs, zoom, lecteur d’écran).
2. Chronométrer les trois scénarios de caisse sur données isolées, cinq passages chacun ; vérifier doubles soumissions et retour navigateur (lot 4).
3. Générer et inspecter les PDF ReportLab, y compris tableaux multipages (lot 5), puis achever les petits contrôles d’accessibilité et la recette finale.
4. Avant exploitation : SMTP, HTTPS/serveur WSGI, protection des tentatives de connexion, supervision et sauvegardes ; voir `../EXPLOITATION.md`.

## Non réalisé ou incertain

Pas de multi-tenant, SaaS rizicole, paiement partiel, intégration prestataire, comptabilité générale, prescription automatique, mode hors ligne complet ou scanner caméra. Assertions communes navigateur validées, mais pas de recette visuelle/métier exhaustive, de conformité WCAG 2.2 AA attestée, de certification fiscale ni de déploiement de production démontré. Le fonctionnement des ressources locales n’implique pas une application hors ligne.

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

## Reprise QA — lot 1, 30 octobre 2026

- Lecture du code : `forms.js` ne traite que les POST ; contrairement à l'hypothèse initiale, il ne met pas le GET du dashboard en noValidate. Aucun changement applicatif déduit des traces encore insuffisantes.
- Nouveaux fichiers/modifications de test : `tools/ux_lot1_diagnose.cjs`, option `--diagnose-lot1` de `tools/run_ux_review.py`. Captures/JSON propres à chaque tentative ; aucune dépendance ajoutée.
- Tentative de diagnostic réellement exécutée : socket refusée avant navigateur, rapport `/tmp/pharmagest-ux-report-ghyjmdhn`. Les douze reproductions restent non exécutées ; attendre le rapport du poste utilisateur. Lots 2 à 7 non terminés ; lot 8 non autorisé et non commencé.

Vérification actuelle sur la copie `fix/recette-frontend` : **85 tests Django réussis en 158,053 s**, check Django sans anomalie, `makemigrations --check --dry-run` sans changement, **12 tests cashier_math + 9 tests operation_math réussis**, syntaxe Node et compilation Python valides. Préparation : **45 rendus serveur**. Ces résultats ne valident pas les douze cas navigateur non exécutés. Commit de test : `a83f1df`. La branche sera transférable par bundle local ; aucun merge ni push effectué et main du dépôt actif préservé.

### Rapport utilisateur 426mt8qc — lot 1

Branche fix/recette-frontend importée et active dans le dépôt utilisateur à 5db7d4a. Rapport lu : 11 OK / 1 KO ; assistant 4/4, dashboard 7/8. KO unique : souris à 360 px sans scripts applicatifs, dates valides, URL inchangée et focus sur date de fin. Cause indéterminée, aucun correctif applicatif. Diagnostic de ce seul cas sur cinq passages préparé, avec traces de navigation, événements/positions et capture avant activation. Syntaxe Node, compilation Python et diff vérifiés ; nouvelles observations navigateur non exécutées ici. Aucun nouveau passage complet des tests Django pour ces seules modifications d'outillage.

## Lot 2 en cours — après rapport 8d0__y96

L'utilisateur autorise le report du clic de période sans JS (4 KO / 5, cause non démontrée) afin de continuer. Nouveau mode `--matrix` : 45 routes × deux thèmes × quatre largeurs × deux modes JS = 720 cas prévus pour cinq rôles. Assertions de présentation, captures et résultats par cas, poursuite malgré les défauts de page/rôle. Aucune promesse de recette métier complète : défaut connu et inspections manuelles restent déclarés.

Tentative locale réelle : socket refusé avant navigateur, rapport kfbqsr68. Nouvelle commande sur le poste : `.venv/bin/python tools/run_ux_review.py --matrix`. Les résultats restent non exécutés jusqu'au retour du poste. Aucun correctif produit, vue/service/modèle/permission/migration modifié.

Vérification de la préparation du lot 2 : 45 rendus serveur réussis via `--prepare-only` (rapport 9yh2w_nv), syntaxe Node du nouveau script, compilation Python et diff sans erreur. Aucun passage navigateur de la matrice réussi ni revendiqué ici.

## Hypothèse serveur de recette et métadonnées — 30 octobre 2026

- Serveur de recette mono-thread confirmé par lecture ; comparaison instrumentée single/threaded (ThreadedWSGIServer Django), journaux connexions/en-têtes/réponses UTC dans requests.jsonl et compteurs/passage dans summary.json. Threaded devient le défaut du lanceur, single reste disponible comme témoin ; cause du défaut non démontrée.
- Tentatives 10 puis 20 passages : refus de socket avant écoute, zéro passage navigateur exécuté et zéro requête HTTP reçue ; rapports n01o0e0c et 01vc845r. Exécuter les deux commandes du guide RECETTE_UX sur le poste et attendre les deux rapports avant de conclure.
- Favicon SVG local et lien global ajoutés ; meta theme-color clair/sombre et synchronisation manuelle/système/onglets. SVG servi en 200 dans un test WSGI sans socket ; comportement automatique favicon du navigateur non vérifié.
- Contrôles réels : trois tests Python d'outillage, cinq tests Node du thème, 21 tests JS existants ; 12 tests Django ciblés, puis deux tests métadonnées après ajout du test statique ; check, syntaxe et compilation sans anomalie. Suite complète non rejouée. Aucune vue/modèle/service/permission/migration modifié, aucun push.

## Retour comparatif réel — 2 novembre 2026

- Rapports _0hmnjzp/e8jza826 : single 1 OK/9 KO (85 requêtes toutes terminées), threaded 0 OK/20 KO (154 requêtes toutes terminées). Aucune connexion acceptée sans en-têtes. Un GET de période en single, aucun en threaded. Les 29 KO précèdent le GET et signalent l'attente de stabilité du clic ; validité du formulaire vraie.
- L'hypothèse préchauffage/serveur n'est pas soutenue par ce comparatif. Aucune cause alternative encore démontrée et aucun correctif produit justifié.
- Nouveau témoin sans serveur ni base : `--probe-browser`, bouton statique, JS/sans JS, rAF/géométrie/focus, versions et traces sans authentification. Écart de versions observé (Playwright 1.50.1/Chrome 145 ; package prévu pour Chromium 133), à vérifier avec le témoin avant toute conclusion.
- Tentative locale : Chrome bloqué au lancement, rapport wjqmsqcq. Syntaxe, compilation, trois tests de journalisation (0,125 s) et diff validés ; aucun cas navigateur de ce témoin exécuté. Commande poste : `.venv/bin/python tools/run_ux_review.py --probe-browser`. Pas de push ni changement métier.

## Témoin navigateur reçu — 2 novembre 2026

Rapport m7tpz2it : clic normal réussi dans les deux cas JS/sans JS, géométrie stable. Pas de panne générale du locator ni de preuve de causalité de l'écart de versions. rAF main-world=0 sans JS malgré clic réussi, donc ne pas en déduire une panne de Playwright. Étape suivante : témoin étendu comparant viewport/hors écran et défilement auto/smooth, six cas à exécuter via --probe-browser. Règle smooth de Bootstrap confirmée par lecture, causalité encore à démontrer ; aucun correctif applicatif.

## Condition isolée et correctif du défilement — 2 novembre 2026

Rapport olrbhn5i inspecté : six variantes de témoin, cinq clics locator OK et un KO uniquement hors écran/smooth/sans JS ; géométrie document fixe. La règle Bootstrap smooth est présente dans le produit. Correctif minimal appliqué dans app.css : root scroll-behavior:auto ; diagnostic enrichi de la valeur calculée. Aucun changement de formulaire, vue, modèle, service, permission ou migration.

La condition est démontrée sur témoin, succès après correction sur l'application toujours à mesurer : demander vingt passages du diagnostic réel. Ne pas transformer l'attendu vingt OK en résultat. Les six variantes ne démontrent pas la cause de l'ancien incident d'assistant ; les quatre essais assistant du rapport 426mt8qc étaient OK, sans reproduction de cet ancien incident.

Contrôles après correction : 13 tests ciblés réussis (23,291 s), check Django, syntaxe Node et diff sans erreur. Validation du clic après correction toujours attendue sur le poste.

## Clic résolu, recette complète en cours — 2 novembre 2026

Rapport dbxll7ue vérifié : 20 exécutés/20 OK/0 KO, scrollBehavior=auto, vingt GET de période parmi 174 requêtes. Comparatif threaded avant/après : 0/20 puis 20/20 ; condition smooth/sans JS/hors viewport isolée par le témoin. Défaut précis clos dans le périmètre testé.

Le mode --matrix est actualisé : le défaut n'est plus déclaré ouvert et le statut de réussite automatique distingue l'examen manuel encore attendu. Tentative locale wvpnl77f : socket refusé, aucun cas navigateur exécuté ; commande poste --matrix. Syntaxe Node, compilation Python et diff vérifiés. Aucun nouveau changement applicatif, commit, merge ou push pour cette reprise.

## Matrice complète vérifiée — 2 novembre 2026

Rapport uwt80wl_ : 720/720 pages OK selon assertions communes, cinq rôles, quatre largeurs, deux thèmes, JS/sans JS ; 1534 HTTP reçus, 720 captures présentes. Détail complet et empreintes des JSON ajoutés à RECETTE_UX. Inspection manuelle de trois captures : défaut de compression du tableau de stocks à 768 px malgré le passage automatique. Retouche minimale de largeur/colonnes appliquée, validation serveur réussie (un test, 2,044 s) ; nouvelle recette ciblée --matrix --role stock et examen de captures à faire après cette retouche.

Checkpoint QA commit possible en distinguant ce qui est vérifié de ce qui reste : pas de validation exhaustive visuelle, lecteur d'écran, impression/PDF ni chronométrage de caisse. Avant de clore la retouche stocks, attendre sa capture récente. Aucun commit/push exécuté lors de cette vérification.

Contrôles actuels du checkpoint : **87 tests Django réussis (157,887 s)**, **3 tests Python d'outillage** et **26 tests JS** réussis ; check Django, `makemigrations --check --dry-run` et diff sans anomalie. Les 720 réussites navigateur précèdent la retouche stock ; ne pas la considérer visuellement validée sans nouvelle capture.

## 2 novembre 2026 — Contrôle stocks et intégration autorisée

Rapport 4_0pr859 vérifié : 144 cas du rôle stock, tous OK après retouche du tableau. Cette réussite automatique ne remplace pas l'examen visuel exhaustif. L'utilisateur autorise maintenant le commit dans fix/recette-frontend puis la fusion dans main, sans demande de push. Tentative git add refusée : .git/index.lock en lecture seule. Aucun commit ni fusion effectué dans le dépôt actif par l'agent ; commandes à exécuter dans le terminal utilisateur.

## 2 novembre 2026 — Lot 3, présentation

Inventaire source : 43 couleurs littérales dans app.css/experience.css, 39 tokens et quatre effets RGB légitimes ; aucune correction de couleur déduite sans mesure rendue. Stocks 768 px récents visuellement lisibles. Ajout de mesures DOM de contrastes et d’impression HTML, sans dépendance ni fichier applicatif modifié. Cinq tests de calcul réussis ; check Django, syntaxe Node/Python et diff vérifiés. Mesures navigateur non exécutées (socket refusée) ; rapport/commande dans RECETTE_PRESENTATION. Pas de nouveau passage des 87 tests Django pour ces seuls outils/documentation. Aucun commit, fusion ou push.

## 2 novembre 2026 — Checkpoint présentation après rapport hôte

Rapport kqi1nqyl analysé : administrateur 176/176 OK, 176 captures, 342 HTTP terminés ; 11 536 mesures de contraste au repos >=4,5:1 (minimum 5,4348), huit contrôles désactivés exclus. Douze impressions générées ; trois PDF monochapitre convertis et inspectés : lisibles, fond clair et montants français. Colonnes Actions vides et liens de téléchargement restent sur papier. Les autres rôles, multipage, états, zoom et PDF ReportLab restent ouverts. Détail et empreinte dans RECETTE_PRESENTATION.md. Cinq tests JS réussis, check/syntaxe/compilation/diff sans anomalie ; suite Django complète non rejouée. Commit autorisé, création de branche test/recette-presentation refusée (.git en lecture seule) ; aucun commit/merge/push par l’agent.
