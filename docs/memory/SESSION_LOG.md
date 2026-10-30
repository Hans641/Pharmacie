# Journal synthétique des sessions

Conserver ici les jalons et preuves, sans secrets ni copie des échanges. Les dates des commits proviennent de Git ; les échanges antérieurs non datés sont rattachés aux jalons seulement lorsque corroborés.

## 28 octobre 2026 — Base du projet

- Commit `19ed046` : initialisation de PharmaGest Django à partir du cahier des charges pharmacie.
- Fonctionnalités métier, tests et guides présents dans le dépôt ; leur état actuel est recontrôlé dans DEVELOPMENT_STATUS.
- L’historique accessible mentionne une erreur « pas un dépôt git » lors de la publication initiale. L’état actuel confirme un dépôt sur main avec un remote GitHub ; ne pas relancer `git init`.

## 29 octobre 2026 — Refonte UI et opérations

- Audit UX, ressources locales, composants partagés, aide aux formulaires et prévisualisations d’opérations présents dans le code et les guides.
- Commit `137b502`, fusion `6a5426f` : formulaires guidés et opérations de stock.
- Restrictions Git rencontrées par l’agent : préparation en copie temporaire et application via bundle côté utilisateur. Les détails d’intégration restent dans les artefacts locaux ignorés `.publication/`.

## 29 octobre 2026 — Caisse

- Commit `c6ec3c6`, fusion `c3026db` : ouverture rapide comptoir, estimation FEFO/panier, aide exacte à la monnaie, contrôles UI paiement/ordonnance et raccourcis.
- Règles métier maintenues ; recette décrite dans `../RECETTE_CAISSE.md`.
- La recette navigateur complète et l’objectif de 30 secondes ne sont pas démontrés par l’historique accessible.

## 30 octobre 2026 — Mémoire persistante

- Demande : instructions permanentes et mémoire de reprise, sans modification applicative ni commit/push.
- Divergence identifiée : la demande cite Laravel Rizicole SaaS/Eloquent ; code et PDF confirment PharmaGest Django sans multi-tenant. Documentation fondée sur ce dépôt, sans inventer de fonctionnalité rizicole.
- Analyse : modèles, migration, routes, vues, services, formulaires, admin, rôles, PDF, tests, guides, cahier des charges et historique Git/conversation accessibles. Les cinq fichiers mémoire existaient vides ; aucun AGENTS.md racine préexistant.
- Création d’AGENTS.md et remplissage des cinq fichiers mémoire ; règles explicites de reprise, vérification et mise à jour après tâche importante.
- Vérification : 79 tests Django réussis (158,296 s), 21 tests JS réussis, check Django sans anomalie et aucune différence de migration. ReportLab absent : moteur de secours testé dans cet environnement.
- Dernier jalon applicatif vérifié : fusion caisse `c3026db`. Prochaine action recommandée : recette navigateur de caisse isolée, puis dashboard. Aucun fichier applicatif ni migration modifié par la tâche documentaire.

## 30 octobre 2026 — Reprise UI : tableau de bord

- Inspection de la mémoire et du dashboard existant avant modification ; caisse déjà intégrée, alertes et classements déjà présents.
- Modification de `templates/pharmacy/dashboard.html` et `static/css/app.css` : séparation situation actuelle/période, navigation par ancres conditionnée aux droits, dates explicites et retour au mois courant, limites des aperçus annoncées.
- Ajout de `docs/RECETTE_DASHBOARD.md` avec avant/après et recette manuelle ; mémoire mise à jour. Aucun fichier métier, modèle, vue ou migration modifié.
- Vérification : `manage.py check` sans anomalie ; 11 PresentationTests réussis (20,401 s), puis deux InterfaceTests ciblés (rendu des pages et refus des accès) réussis (3,841 s). `git diff --check` sans erreur. Suite complète non réexécutée pour cette modification de présentation.
- Recette navigateur responsive/clavier encore non exécutée ; aucune conformité visuelle revendiquée. Aucun commit, fusion ou push effectué. Prochaine étape : recette dashboard/caisse puis amélioration des stocks selon les constats.

## 30 octobre 2026 — Recette du tableau de bord et préparation Git

- Autorisation utilisateur : vérifier l'interface, committer dans une branche puis fusionner dans main. Aucun push demandé.
- Ajout de trois tests serveur et extension du script navigateur pour ancres clavier, filtre de dates et repli sans JS ; détails dans RECETTE_DASHBOARD.
- Le premier passage a révélé une attente incorrecte du nouveau test : le gestionnaire de stock possède bien `view_purchase` et doit conserver la période des achats. Attente corrigée, aucune permission modifiée ; les trois nouveaux tests passent.
- Chrome ne démarre pas dans le bac à sable (`setsockopt: Operation not permitted`). Recette visuelle à 360/768/1280/1920 px et chronométrage caisse non attestés. Aucun changement sur la base active.
- Création de branche dans le dépôt actif refusée : `.git` en lecture seule. Préparation autorisée dans une copie temporaire ; bundle et finaliseur locaux pour application par l'utilisateur sans remplacer les fichiers de travail. Ne pas annoncer main fusionné avant vérification du dépôt actif.

- Validation finale après correction du test : suite complète **82 tests Django réussis (153,801 s)** ; **12 tests cashier_math + 9 tests operation_math réussis** ; check Django, vérification des migrations, syntaxe du script navigateur et diff sans erreur.
- Commits mémoire et UI, puis fusion sans fast-forward, préparés sur `feat/dashboard-clarity` dans une copie isolée. Empreintes et identifiants disponibles dans `.publication/dashboard-merge-manifest.json` ; application au dépôt actif via `.publication/finaliser-dashboard.py` depuis le terminal utilisateur. Le code métier reste inchangé.

## 30 octobre 2026 — Interface des stocks et lots

- Reprise à main `14c7c6d` : fusion dashboard confirmée, référence locale origin/main identique ; pas de vérification distante. Échec DNS du push précédent de l'agent conservé comme fait historique.
- Inspection du template stock, du filtre serveur, de l'ordre du modèle Lot, des badges, de la recherche progressive et des tests existants. Menus de ligne, badges et cartes mobiles déjà présents, donc conservés.
- Ajout de filtres rapides préservant la recherche et réinitialisant la page, libellés visibles, compte filtré, tri annoncé, aide dépliable, mentions lot épuisé/exclu de la vente, liens de fiche selon permission et réinitialisation après absence de résultat. Sprite et CSS locaux complétés.
- Trois tests ajoutés : conservation de recherche/pagination des raccourcis, états cumulés et quantité zéro, liens interdits absents pour un lecteur de lots sans autre permission.
- Vérification : 15 tests Django ciblés réussis (28,454 s), couvrant StockClarityTests, PresentationTests et le rendu des pages principales ; check Django sans anomalie, diff sans erreur. Suite complète non réexécutée : modification de présentation seulement, aucune vue/service/modèle/migration modifié. Recette navigateur toujours à effectuer, voir RECETTE_STOCKS.
- Aucun commit, merge ou push pour cette itération. Prochaine étape : recette stocks aux quatre largeurs, puis cohérence des listes restantes selon les constats.

## 30 octobre 2026 — Recette responsive et clavier isolée

- Reprise à main `7c871d3`, propre, fusion stocks confirmée ; référence locale origin/main identique, push déclaré effectué par l'utilisateur sans nouvelle interrogation distante.
- Nouvelle tentative Chrome : échec avant rendu (`setsockopt: Operation not permitted`). Aucun outil navigateur externe disponible. Lancement complet du nouveau harnais : ouverture de socket locale refusée avant exécution de Playwright ; rapport d'échec conservé sous /tmp.
- Ajout de `tools/run_ux_review.py` : base/médias temporaires, cinq rôles, données fictives à noms longs, lot bloqué/épuisé/périmé/proche, réception partielle, paniers avec ordonnance. Identifiants générés et mot de passe en mémoire uniquement. Serveur local dédié sur port libre, nettoyage et rapports séparés. Préparation des paniers par administrateur de test pour respecter les rôles de consultation.
- Mode `--prepare-only` vérifié : 45 rendus serveur pour cinq rôles. Contrôle externe avec DATABASE_PATH sentinelle : valeur héritée ignorée, sentinelle et empreintes base active/médias identiques avant/après.
- Script Playwright complété : activation clavier du lien d'évitement, boucle Tab/Maj+Tab du tiroir, captures menu, contrôles de débordement et captures sans JS aux quatre largeurs, conservation du résultat partiel et d'une capture en cas d'échec après lancement. Syntaxe Node valide ; nouvelles assertions navigateur non exécutées.
- Suite complète : **85 tests Django réussis (158,444 s)** ; **21 tests JS réussis** ; check Django, compilation Python, syntaxe Node et diff sans anomalie. Aucun fichier métier ou template applicatif modifié.
- Recette visuelle toujours non validée. Prochaine action nécessaire hors bac à sable : `.venv/bin/python tools/run_ux_review.py`, inspecter le dossier de résultats annoncé, puis corriger les défauts mesurés. Guide RECETTE_UX actualisé. Aucun commit, fusion ou push effectué pour cette tâche.

## 30 octobre 2026 — Correction après premier rapport navigateur hôte

- Lecture du rapport `/tmp/pharmagest-ux-report-sn78_rcg` et inspection de la capture echec.png. Administrateur : 11 pages à 360 px et dashboard à 768 px réussis avec JS ; échec catalogue à 768 px. Aucun résultat extrapolé aux autres rôles/largeurs ni au repli sans JS.
- Capture : noms, badges et actions morcelés par compression des colonnes. CSS corrigé : largeur minimale de catalogue au-dessus de 600 px, défilement interne, mots préservés, actions de cartes sur une colonne.
- Contrôle : descendants de details fermés exclus des mesures ; premier menu ouvert par Entrée, liens visibles et dimensions 44 px contrôlés, absence de débordement ouvert puis fermeture. Seuil tactile préservé ; aucune assertion navigateur nouvelle déclarée réussie avant relance hôte.
- Vérification : 11 PresentationTests réussis (20,365 s), syntaxe Node et diff sans erreur. Le favicon 404 n'est pas la cause de l'assertion. Nouvelle exécution du lanceur nécessaire. Aucun commit/push.

### Retour hôte z_0k5lok — 30 octobre 2026

Le catalogue à 768 px passe après correction ; 20 parcours de page avec JS sont enregistrés comme réussis pour l'administrateur (11 à 360 px, neuf à 768 px). Arrêt sur la création de médicament : le scénario attend le champ prix alors que la capture montre toujours Identification. Cause exacte du non-avancement non démontrée. Le scénario active maintenant Continuer au clavier et vérifie l'étape atteinte, avec restitution des messages inline si elle reste bloquée. Aucun changement de validation applicative. Syntaxe Node et diff vérifiés ; nouvelle exécution hôte requise, les autres rôles et le sans-JS restent non validés.

## 30 octobre 2026 — Thème sombre global

- L'utilisateur réoriente le travail vers le mode sombre après un nouvel échec de recette. Rapport `6zmmb904` lu : clic sur Appliquer la période instable, distinct du problème précédent de champ de prix caché. Recette générale laissée incomplète.
- Ajout de themes.css, theme.js et du contrôle Système/Clair/Sombre partagé en pied de page. App.css et experience.css utilisent des tokens pour les composants à couleurs figées ; base.html charge le thème et annonce les deux schémas. Impression claire conservée et largeur minimale du catalogue levée pour le papier.
- Préférence locale non sensible seulement, contrôle masqué sans JS, préférence système en CSS ; palette écran commune aux pages, y compris authentification. Aucun modèle/vue/service/permission/migration modifié.
- Contrôles : 12 tests de présentation/rendu réussis (22,704 s), check Django, syntaxe JS et diff sans erreur ; 17 paires par palette >=4,5:1, focus et bordure de champ >=3:1 sur surface ; comportement de préférence/synchronisation/stockage bloqué vérifié en VM Node, sans navigateur.
- Guide MODE_SOMBRE créé avec fichiers, couverture, ratios et recette. Validation visuelle sombre, états natifs réels et impression encore à faire. Aucun commit/push. Prochaine action : choisir Sombre en pied de page sur le serveur utilisateur et examiner les écrans.
