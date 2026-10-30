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
