# État du développement

Dernière reprise vérifiée : **4 novembre 2026**, main à `2c02668`, fusion recette finale confirmée ; outils de recette manuelle non commités, contrôles HTML OK ; essais humains déclarés effectués sans détails, temps humains non transmis et impression physique non exécutée.

## Fonctions implémentées et preuves disponibles

| Ensemble | Preuves | Limites |
|---|---|---|
| Auth, rôles, comptes, CSRF, accès | vues/formulaires/setup_roles ; InterfaceTests et tests de permissions | SMTP réel et protection anti-bruteforce non validés |
| Catalogue, catégories, fournisseurs, clients, photos et archivage | modèles/forms/entity_* ; tests images, recherche, historique et accès | Pas de recette utilisateur complète attestée |
| Achats et réceptions partielles | services et tests reliquat, rollback, réception unique | Écran de réception par ligne ; service accepte plusieurs lignes |
| Lots, FEFO, inventaire et mouvements | services, BusinessTests | PostgreSQL et forte charge non testés |
| Vente, paiement intégral, ordonnance, concurrence | tests atomicité, stock, historique, double validation et concurrence | Électronique manuel ; pas de réservation globale des brouillons |
| Retours et remise en stock contrôlée | tests quantité, idempotence, lot périmé et historique | Remboursement exécuté hors logiciel |
| Dashboard et PDF | code de calcul, tests de rendu et signature PDF | 11 PDF/23 pages inspectés avec ReportLab ; conformité fiscale non établie |
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

1. Relire/enregistrer le lot recette par rôle et bilan ; main observé à 60a9aea, outils/docs/hygiène non commités. Commit en branche dédiée et fusion main autorisés ensuite ; création de branche refusée en lecture seule, commandes utilisateur nécessaires. Aucun push autorisé.
2. Compléter lecteur d’écran, ordre complet du clavier et combinaisons de zoom/texte seul non attestées.
3. Mesurer humainement cinq ventes par scénario ; les temps automatisés ne suffisent pas.
4. Tester l’impression physique et préparer l’exploitation si nécessaire ; voir BILAN_FRONTEND.md et EXPLOITATION.md.
5. Évolutions fonctionnelles optionnelles : plans uniquement dans BILAN_FRONTEND, aucun changement de vue autorisé.

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

## 2 novembre 2026 — Impression : retouches en attente de recette

Branche active test/recette-presentation, commit bbe1005 confirmé ; main reste à 3b28d08. Correction minimale des colonnes Actions et invites PDF imprimées (trois templates), assertions navigateur correspondantes ajoutées. 11 tests de présentation réussis (20,248 s), cinq tests JS réussis, check/syntaxe/diff sans anomalie. Recette après correction non exécutée : socket refusée, rapport 2obe37jh, zéro requête. Prochaine commande poste : `--matrix --presentation`, cinq rôles ; inspecter les nouvelles impressions. Aucun nouveau commit/merge/push. Détail avant/après dans RECETTE_PRESENTATION.md.

## 2 novembre 2026 — Recette présentation des cinq rôles vérifiée

Rapport hôte 5wjmy_iw vérifié : cinq rôles, 720/720 cas OK, 720 captures, 1 534 HTTP terminés, 47 038 mesures de contraste au repos >=4,5 (minimum 5,4348), 24 contrôles désactivés exclus. Les 52 PDF HTML sont présents et tiennent chacun sur une page ; texte extrait de tous sans colonne Actions ni invite de téléchargement. Trois PDF sombres administrateur convertis et inspectés : retouches visuellement confirmées. Détail/empreintes dans RECETTE_PRESENTATION.md. Multipage, reçu encaissé, ReportLab, états exhaustifs, zoom et lecteur d’écran restent ouverts. Aucun nouveau test applicatif ni commit/merge/push pour cette analyse.

## 2 novembre 2026 — Recette authentification/erreurs préparée

Main propre à 9bf65ad avant tâche : fusion précédente confirmée. Nouveau mode --accessibility, 112 cas prévus (connexion/réinitialisation et rendus isolés des templates 403/404/500). Vérifications clavier, mot de passe, erreurs locales, contrastes et mouvement réduit ; aucun POST navigateur. Tentative ru1ddq2f bloquée par socket avant serveur, zéro cas exécuté. Cinq tests de calcul, check Django, syntaxe et diff valides ; suite Django complète non rejouée. Prochaine commande hôte : `.venv/bin/python tools/run_ux_review.py --accessibility`. Zoom réel, lecteur d’écran, handlers d’erreur HTTP et autres interactions restent ouverts. Détail dans RECETTE_PRESENTATION.md. Aucun changement applicatif ni commit/merge/push.

## 2 novembre 2026 — Rapport accessibilité e5mzo9ly : arrêt commun au focus

Rapport lu : 112/112 KO, tous à l’assertion « Focus visible », outline calculé 0px/none sur le premier bouton. Les assertions suivantes (survol, mot de passe, validation locale et contrastes) n’ont pas été atteintes. Ne pas assimiler ces résultats à 112 défauts indépendants.

Cause de cascade confirmée dans Bootstrap local : `.btn:focus-visible` impose `outline:0`, plus spécifique que la règle générique `:focus-visible` de app.css. Un box-shadow Bootstrap peut exister : le rapport précédent ne le mesurait pas, donc aucune conclusion d’absence totale d’indicateur. Correction : règle `.btn:focus-visible` de même spécificité après Bootstrap, contour de 3px avec le token focus. Script corrigé pour activer explicitement la modalité clavier, enregistrer activeElement/:focus-visible/box-shadow et afficher les erreurs dans le terminal. Aucune suppression de l’assertion ni changement métier.

Syntaxe Node, check Django et diff vérifiés. La validation navigateur après correction reste à obtenir ; commande : `.venv/bin/python tools/run_ux_review.py --accessibility`. Aucun succès après correction revendiqué, aucun commit/merge/push.

## 2 novembre 2026 — Rapport faugqo54 : 104 OK / 8 KO

Rapport accessibility.json lu : 104 réussites et huit échecs, exclusivement connexion sans JS aux quatre largeurs et deux thèmes. Dans les huit cas, active=false et :focus-visible=false. Le sélecteur `main .btn` choisissait le bouton Afficher du mot de passe, présent dans le template mais hidden sans JS ; le template includes/field.html et le script app.js confirment ce repli intentionnel. Le script essayait donc de focaliser un contrôle masqué. Aucun défaut produit déduit de ces huit échecs.

Correction d’outillage uniquement : `main .btn:visible`, ajout du libellé du contrôle mesuré au diagnostic. L’assertion exigeant que le bouton Afficher soit masqué sans JS est conservée, ainsi que tous les contrôles de focus. Les 104 cas réussis confirment le contour de focus de 3px dans le périmètre testé ; les assertions après l’échec des huit cas n’ont pas été exécutées.

Syntaxe Node et git diff --check vérifiés. Validation après cette dernière correction encore attendue : `.venv/bin/python tools/run_ux_review.py --accessibility`. Aucun nouveau test Django complet, commit, merge ou push. Ne pas transformer 104 réussites et huit corrections attendues en 112 réussites mesurées.

## 2 novembre 2026 — Accessibilité complémentaire validée sur l’hôte

Rapport f2gyt6jp inspecté : 112/112 OK, 112 captures, focus actif/contour 3px dans tous les cas ; 1 024 ratios >=4,5 (minimum 5,6320), seize vérifications d’erreurs locales JS, 1 064 HTTP terminés. Deux captures sombres examinées (connexion sans JS 360 et template 500 JS 768). Défaut de contour et faux échec du bouton hidden clos dans le périmètre testé. Zoom réel 200 %, lecteur d’écran, dialogues métier, handlers HTTP réels et liens de réinitialisation restent ouverts. Tableau et empreinte dans RECETTE_PRESENTATION.md. Aucun nouveau test applicatif ni commit/merge/push.

## 2 novembre 2026 — Recette humaine zoom/clavier préparée

Ajout de tools/run_manual_review.py : réutilisation de la préparation fictive isolée et du serveur threaded existants, mot de passe temporaire saisi sans écho (jamais journalisé), serveur ouvert jusqu’à Entrée/Ctrl+C puis nettoyage. Aucun fichier applicatif modifié. Protocole détaillé dans docs/RECETTE_ZOOM_CLAVIER.md : commencer à 1280 px, zoom navigateur réel 200 %, caisse/formulaire, dialogue inventaire annulé par Échap/Revenir, puis autres thèmes/largeurs et texte seul. Résultats manuels non exécutés, utilisateur requis. Aide CLI, compilation Python et diff vérifiés ; serveur interactif et parcours navigateur de ce lanceur non exécutés ici. Aucun commit/merge/push.

## 2 novembre 2026 — Début du lot chronométrage

L’utilisateur indique les trois parcours manuels zoom/clavier réglés et demande de passer au point suivant. Retour utilisateur consigné sans inventer navigateur, dimensions, captures ou mesure instrumentée ; les combinaisons restantes restent non attestées.

Ajout de run_cashier_benchmark.py/ux_cashier_benchmark.cjs : quinze ventes fictives isolées, trois scénarios, caissier/espèces, recherche au clavier et confirmation HTML avec lien reçu, horloge navigateur continue entre navigations ; médiane/min/max et audits paiements/stock. Protocole manuel et limites dans RECETTE_CAISSE.md. Le PDF n’est pas ouvert dans le temps mesuré ; doubles soumissions/retour restent séparés. Tentative o1xxdqyh refusée au socket, aucune durée mesurée. Syntaxe, check Django, diff et douze tests JS caisse validés. Aucun changement métier ni commit/merge/push.

## 2 novembre 2026 — Checkpoint clavier et chronométrage autorisé

Rapport didge5bc vérifié : 15/15 ventes automatisées OK, quinze paiements uniques, stocks conformes, quinze captures présentes. Médianes : simple 2,126 s, trois produits 4,345 s, ordonnance 2,082 s. Résultats/empreintes et bornes dans RECETTE_CAISSE.md ; aucune preuve de vitesse humaine ni doubles soumissions déduite. Recette complémentaire précédente f2gyt6jp : 112/112 OK.

Utilisateur autorise commit en branche secondaire puis fusion main, sans push. Vérifications syntaxe Node/Python, check Django et diff sans erreur ; pas de nouveau passage complet Django. Tentative de création fix/qa-clavier-chronometrage refusée sur refs .git en lecture seule : aucun commit ni fusion effectué par l’agent. Commandes à exécuter dans le terminal utilisateur. Modèles/vues/services/permissions/migrations inchangés.

## 2 novembre 2026 — Recette des doubles soumissions préparée

Fusion précédente vérifiée sur main à aec1e78, dossier propre avant travail. Extension du lanceur de caisse : --resubmission et nouveau ux_cashier_resubmission.cjs, douze cas (double clic, Entrée répétée, retour × JS/sans JS × 360/1280). Rejeu POST après succès et audit final paiements/mouvements/stock ; aucune modification métier. Tentative ru0zmd5r bloquée à la socket, aucun cas navigateur exécuté. Syntaxe, check Django, diff et douze tests JS caisse validés ; suite Django complète non rejouée. Protocole et limites dans RECETTE_CAISSE.md ; commande hôte --resubmission. Aucun commit/merge/push.

## 2 novembre 2026 — Double soumission : dix succès et deux attentes KO

Rapport t0w3pe_s : 10/12 scénarios OK. Les deux KO Entrée répétée JS expirent en observant disabled avant la répétition ; cause non démontrée. Audit final des douze ventes conforme (paiement unique, mouvement -1, stocks 88/100/100), sans clôturer les deux scénarios. Ajout de diagnostics lockBeforeWait/lockAfterWait et observation par minuterie au lieu du polling rAF pendant la requête retenue ; exigence de désactivation conservée. Syntaxe et diff vérifiés ; commande hôte --resubmission à relancer. Aucun fichier applicatif, commit/merge/push. Détail et empreinte dans RECETTE_CAISSE.md.

## 2 novembre 2026 — Rapport x90n9jdd : attente circulaire du test

Rapport lu : 10/12 OK, deux KO Entrée répétée avec JS. L’erreur précise est désormais `locator.evaluate: Timeout ... waiting for ... navigation to finish`, avant tout relevé lockBeforeWait. Les autres scénarios et dix rejeux passent ; audit des douze ventes toujours conforme, stocks 88/100/100. Les deux cas répétés JS restent non vérifiés.

Cause démontrée pour ce dernier blocage : le test retient le POST jusqu’à observation du bouton, mais Locator.evaluate attend cette navigation retenue. L’hypothèse antérieure d’un simple polling rAF ne suffisait pas à expliquer le nouvel échec. Correction d’outillage : acquérir ElementHandle avant soumission puis évaluer cette référence au document courant, sans résolution de locator attendant la navigation. Attendre la mutation disabled avec MutationObserver et une échéance d’échec de 10 s, sans sleep/polling rAF ; exiger disabled=true, submitting=true et aria-busy=true. Les frappes répétées et assertions de paiement/stock restent inchangées. Aucun correctif applicatif justifié.

Syntaxe Node et diff vérifiés. Nouvelle recette navigateur non exécutée ici (restriction socket) ; relancer `--resubmission` sur l’hôte et examiner lockBeforeWait/lockAfterWait. Aucun commit/merge/push.

Preuve : `/tmp/pharmagest-cashier-report-x90n9jdd/resubmission.json`, SHA-256 : `037e189df84e9a0279638b4151d9211151c49d87955f6e742c34f29d9998a67e`.

## 3 novembre 2026 — mhqs_qyu : expiration globale, pas une réussite

Rapport lu : quatre doubles clics OK, puis blocage dans le premier scénario Entrée répétée JS ; expiration du sous-processus après **600 s**. Le résumé ancien marquait non exécuté malgré ces résultats partiels. Aucun audit final disponible pour ce passage, ne pas le remplacer par celui d’un ancien rapport. L’affichage du dossier seul n’est pas un verdict de réussite.

L’évaluation via ElementHandle n’a pas supprimé le blocage dans le document en navigation ; sa propre échéance JavaScript n’a pas été observée. Nouveau dispositif : installer la sonde MutationObserver AVANT soumission et transmettre les changements à Node via une binding Playwright. Aucun accès DOM déclenché par le test après le POST retenu. Les états sont enregistrés dans lockEvents au fil des mutations ; échéance de dix secondes côté Node, indépendante de l’horloge du document. L’exigence disabled/submitting/aria-busy reste conservée.

Le lanceur distingue désormais timeout/interrompu de non exécuté et conserve la sortie partielle du navigateur en cas d’expiration. Un cas commencé est marqué « en cours », les suivants restent non exécutés. Aucune modification d’application ni de métier. Syntaxe Node/Python et diff contrôlés ; nouvelle recette hôte nécessaire avant toute conclusion. Commande : `--resubmission`. Aucun commit/merge/push.

Preuve partielle : `/tmp/pharmagest-cashier-report-mhqs_qyu/resubmission.json`, SHA-256 `4ee5b1e5252fe7361726684998023af722aaa9e73311744406bcbb58295f6856`.

## 3 novembre 2026 — wbr2hbqe et collision du champ method

Rapport wbr2hbqe : 10 OK/2 KO, mêmes cas Entrée répétée JS, échéance Node atteinte en 10 s. Les sondes ne reçoivent que l’état initial (disabled=false, submitting/busy absents). Les douze ventes ont néanmoins un paiement et un mouvement -1 uniques, stocks 88/100/100 conformes. Aucune protection JS réussie déduite du seul audit serveur.

Lecture du code : checkout contient les radios name=method, tandis que le gestionnaire commun appelle form.method.toLowerCase(). Une propriété de contrôle nommé peut masquer la propriété du formulaire. Nouveau test VM exécutant le vrai app.js avec ce masquage : deux tests échouent AVANT correctif avec TypeError form.method.toLowerCase is not a function ; le test GET/dialog réussit. Correction minimale : lecture de getAttribute('method') au lieu de form.method. APRÈS : **3/3 tests réussis**, dont verrou synchrone, désactivation différée et prévention du second submit. Il s’agit d’une reproduction contrôlée JS, pas encore de la capture de cette exception dans le navigateur réel.

Les anciens changements d’instrumentation corrigeaient les attentes circulaires, pas cette collision. Recette renforcée : collecte pageErrors et type/classe réel de form.method avant soumission, sans en enregistrer les valeurs. Une exception JS produit un KO. Aucun modèle/vue/service/permission/migration modifié. Les tests Node de régression, syntaxes et diff sont vérifiés ; recette navigateur après correctif toujours non exécutée ici (socket refusée). Relancer --resubmission sur l’hôte avant de clore le défaut. Aucun commit/merge/push.

Preuve : `/tmp/pharmagest-cashier-report-wbr2hbqe/resubmission.json`, SHA-256 `d00a21443f2dfbf014c877f6eba772e65dc2c25ae74281978027b67b296adaa5`.

## 3 novembre 2026 — Doubles soumissions closes dans le périmètre testé

Rapport v2a883_n vérifié : 12/12 OK, douze captures, aucun pageErrors, douze ventes/paiements uniques et mouvements -1 uniques, stocks 88/100/100 conformes. Entrée répétée JS : disabled/submitting/busy attestés et une seule requête ; rejeux et retour navigateur passent. form.method est réellement HTMLInputElement (attribut post), confirmant la collision corrigée par getAttribute. Détail/empreinte dans RECETTE_CAISSE.md. Limites concurrence réelle/charge conservées ; prochaines vérifications PDF ReportLab et multipage. Aucun nouveau test applicatif ni commit/merge/push lors de cette analyse.

## 3 novembre 2026 — Lot PDF ReportLab en préparation

ReportLab absent de .venv. Installation de requirements.txt tentée dans un venv propre /tmp/pharmagest-pdf-review-venv : pip ne trouve aucun paquet Django==6.0.4 ; cause réseau/config exacte incertaine, journal /tmp/pharmagest-pdf-install.log. Aucune génération ReportLab ni réussite visuelle revendiquée.

Ajout de tools/run_pdf_review.py : huit documents réels sur base fictive temporaire, trois fixtures longues de 80 lignes, extraction texte/pdfinfo et conversion de chaque page en image ; verdict visuel laissé en attente. Compilation et garde-fou ReportLab absent exécutés. Protocole/commandes environnement propre dans RECETTE_PDF.md. Aucun correctif applicatif ni nouveau test de contenu PDF effectué avant le rapport visuel. Travaux précédents de doubles soumissions préservés. Aucun commit/merge/push.

## 3 novembre 2026 — Lot PDF : vérification réalisée

Installation utilisateur complète dans /tmp/pharmagest-pdf-env-hote confirmée (ReportLab 4.5.1). Rapport avant kdvafnqq : onze PDF/47 pages, défauts visuels de format anglais, alignement/largeurs et page de mention légale seule démontrés. Correctif de présentation uniquement dans pharmacy/pdf.py, tests textuels pharmacy/test_pdf.py, sans vue/modèle/service/migration modifié.

Rapport après ia7_9zpz généré et inspecté par l’agent : onze PDF/23 pages, toutes les images examinées. Huit documents réels tiennent chacun sur une page ; trois fixtures de 80 lignes tiennent chacune sur cinq pages (contre douze), lignes complètes/uniques, en-têtes répétés, montants français alignés et pagination lisible. Détail avant/après et empreintes dans RECETTE_PDF.md.

Deux tests monétaires échouaient avant correction ; les trois tests PDF passent après (0,234 s). Suite complète dans l’environnement propre : **90 tests Django réussis en 157,198 s**, journal /tmp/pharmagest-reportlab-tests.log, base de test détruite. Check Django sans anomalie, makemigrations --check --dry-run sans changement, diff propre. Moteur de secours également exécuté dans .venv sans ReportLab, extraction référence/accent/ligne/montants français vérifiée. Impression physique/thermique, conformité fiscale et balisage accessible PDF non attestés. Aucun commit/merge/push.

## 3 novembre 2026 — Intégration caisse/PDF autorisée

L’utilisateur autorise les commits dans une branche secondaire puis la fusion main, sans push. État contrôlé : main à aec1e78, seuls correctifs/outils/docs attendus modifiés ; aucun diff sur modèles/vues/services/formulaires/migrations. Log de suite complète confirmé : 90 tests réussis (157,198 s), diff sans erreur. Création de fix/recette-caisse-pdf tentée et refusée sur refs .git en lecture seule. Aucun commit ni fusion effectué par l’agent ; commandes fournies pour le terminal utilisateur, sans contournement des droits.

## 4 novembre 2026 — Parcours finaux par rôle

Reprise Git : main propre à 60a9aea, fusion caisse/PDF confirmée. Nouveau tools/run_role_journeys.py : cinq parcours HTTP authentifiés avec CSRF, neuf refus GET/POST sans mutation et un refus sans CSRF, exclusivement base/médias temporaires. Premier passage 4zyj8bfz : 14/15, assertion de test stock erronée (block attendu au lieu de inventory existant) ; correction de l’outil, aucun changement applicatif. Second rapport p9de2osq : 15/15 OK serveur. PDF servis par le moteur de secours dans cet environnement ; aucune nouvelle preuve ReportLab déduite.

run_manual_review accepte --role all pour tester les cinq comptes dans le même serveur fictif ; protocole dans RECETTE_ROLES.md. Ces parcours navigateur humains sont non exécutés, retour utilisateur attendu. Compilation Python, aide CLI et diff vérifiés ; pas de nouveau passage complet Django pour ces seuls outils/docs. Les preuves historiques 90 tests/23 pages PDF restent datées du lot précédent. Aucun commit/merge/push.

## 4 novembre 2026 — Accès aux comptes de recette à diagnostiquer

L’utilisateur signale un échec de connexion. Dernier journal manuel inspecté : 9587vp_7, serveur annoncé sur 38661, aucune requête de login observée à cet instant ; précédent serveur g_r1uaei/37207 nettoyé. Cela suggère une adresse différente, sans le démontrer tant que l’URL/message utilisateur ne sont pas connus. Aucun diagnostic de mot de passe erroné déduit. Les cinq connexions CSRF du rapport serveur p9de2osq avaient réussi.

Lanceur manuel clarifié : comptes ux_* valables seulement sur son adresse/port, recréés à chaque lancement, terminal à garder ouvert. URL et message d’erreur demandés, aucun mot de passe demandé. Syntaxe et diff contrôlés ; aucune modification applicative, aucun commit/merge/push. Les parcours humains restent non validés.

Diagnostic confirmé par l’URL transmise : tentative sur 127.0.0.1:8000, serveur habituel, tandis que le dernier lanceur manuel annonce 38661. L’utilisateur recevait donc le refus de la base habituelle ; utiliser l’URL de recette annoncée et son mot de passe temporaire. Aucun mot de passe réel ou temporaire consigné. L’accès effectif sur le bon serveur reste à confirmer.

## 4 novembre 2026 — Clôture des parcours par rôle et bilan frontend

Après accès au bon serveur fictif, l’utilisateur confirme les cinq parcours manuels OK. Résultat déclaré, sans version navigateur/dimensions/captures fournies ; tableau RECETTE_ROLES actualisé. BILAN_FRONTEND.md rassemble preuves, défauts corrigés, limites, archive propre et plans des quatre évolutions optionnelles, sans modification de vues ni implémentation.

Contrôles réellement exécutés : suite .venv 90 découverts, 87 exécutés/réussis et 3 ignorés faute de ReportLab (158,595 s), log /tmp/pharmagest-final-frontend-tests.log ; 34 tests JS et 3 tests Python d’outillage (0,241 s) réussis, check sans anomalie, aucune migration détectée. La preuve antérieure 90/90 avec ReportLab reste datée du 3 novembre. .gitignore complété pour les cinq familles de rapports locaux ; chemins .publication/.venv/SQLite/rapports ignorés et non suivis. Diff propre, aucun fichier applicatif modifié pour ce lot. Aucun commit/merge/push.

Restent non mesurés : lecteur d’écran/combinaisons de zoom non attestées, temps humains des ventes, impression physique et certains handlers/reset. Les fonctions optionnelles exigent un périmètre et une autorisation explicites. Le checkpoint est prêt à relire/enregistrer, sans revendiquer une certification globale.

## 4 novembre 2026 — Intégration finale des parcours autorisée

L’utilisateur autorise commit dans une branche dédiée puis fusion main, sans push. État contrôlé : main à 60a9aea, uniquement outils/docs/.gitignore attendus modifiés ; diff propre, fichiers métier protégés sans diff. Résultats de clôture confirmés dans le journal : 87 tests exécutés/réussis, trois PDF ignorés faute de ReportLab, 34 tests JS et trois tests Python d’outillage réussis.

Création de test/recette-finale-roles tentée, refusée sur refs .git en lecture seule. Aucun commit ni fusion effectué par l’agent ; commandes transmises pour le terminal utilisateur, sans contournement des droits.

## 4 novembre 2026 — Accessibilité approfondie commencée

Main propre à 2c02668 avant tâche, fusion précédente confirmée. tools/run_semantic_review.py vérifie les rendus HTML et références ARIA sur base temporaire : rapport kx3q74uq, 50/50 OK (45 pages, trois formulaires invalides, deux anonymes). Quatre témoins unitaires positifs/négatifs réussis via tools/test_semantic_review.py ; check Django, compilation et diff valides. Aucun défaut applicatif identifié, aucun changement d’application. Le parseur ne prouve pas l’arbre accessible ni les annonces vocales.

Orca 46.1 détecté ; Firefox snap installé mais lancement/version refusé dans le bac à sable sur XDG_RUNTIME_DIR. Aucun lecteur d’écran ni zoom humain exécuté par l’agent. Protocole à trois scénarios caisse/formulaire/dialogue puis texte seul dans RECETTE_ACCESSIBILITE_APPROFONDIE.md ; attente des observations utilisateur, pas de réussite inventée. Aucun nouveau passage complet Django ni commit/merge/push.

## 4 novembre 2026 — Passage au chronométrage humain

L’utilisateur dit avoir effectué les essais lecteur d’écran et texte seul puis demande le prochain point, sans verdict détaillé. Consigner « essais déclarés effectués, résultat détaillé non transmis », sans transformer ces messages en validation complète. Nouveau point : quinze mesures humaines de caisse (cinq par scénario), conditions et erreurs à relever sur serveur fictif.

Ajout tools/summarize_manual_timings.py : statistiques de durées déclarées, cinq valeurs strictement positives/finies par scénario, source humaine non observée indiquée. Aide/compilation et contrôles de saisie synthétiques exécutés, aucun rapport humain fictif créé. Protocole actualisé dans RECETTE_CAISSE.md ; .gitignore couvre les rapports sémantiques et humains si copiés à la racine. Aucun temps humain réellement transmis, aucun seuil déclaré atteint. Aucun changement applicatif ni commit/merge/push.

## 4 novembre 2026 — Préparation impression physique et commit demandé

L’utilisateur indique les essais humains de caisse OK sans fournir quinze temps : déroulement déclaré satisfaisant, médianes humaines toujours non mesurées. Il demande le point impression puis un commit. Contrôles locaux : CUPS arrêté et aucune destination par défaut (lpstat), anciens PDF/venv temporaires disparus, ReportLab absent de .venv. Aucune impression envoyée ni réussite papier déclarée.

Nouveau protocole RECETTE_IMPRESSION_PHYSIQUE.md : régénération des PDF fictifs, reçu et commande/réception A4, toutes les pages de la fixture longue, limites du thermique A4 versus largeur réelle. Check Django, compilation des trois outils et quatre tests sémantiques réussis, diff sans erreur ; pas de nouveau passage complet Django pour ce lot d’outillage/docs.

Commit demandé pour les outils/protocoles d’accessibilité, statistiques humaines et impression ; ce checkpoint ne clôt pas les observations manuelles non transmises ni l’impression papier. Aucun changement applicatif. Pas de demande de merge ni push pour ce lot.

Création de branche test/recette-manuelle-finale tentée : refus d’écriture des refs .git (lecture seule). Aucun commit effectué par l’agent ; commandes à exécuter depuis le terminal utilisateur. Aucun contournement, fusion ou push.
