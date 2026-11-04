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

## 30 octobre 2026 — Fusion sombre confirmée et reprise QA par lots

- Git vérifié : main propre à `27ed6f6`, fusion `feat/dark-mode` après `bfad35e`, origin/main local identique. Ces faits remplacent les états « aucun commit » des notes antérieures, conservées comme historique. Pas d'accès distant effectué.
- Consignes et guides relus ; travail limité au lot 1 tant que les causes ne sont pas démontrées. Modèles, vues, services, permissions et migrations préservés ; aucun nouveau composant ni dépendance.
- Création de branche dans le dépôt actif refusée (.git en lecture seule). Copie isolée à /tmp/pharmagest-recette-frontend, branche fix/recette-frontend créée depuis main. Aucun merge/push effectué.
- Diagnostic dédié ajouté : reproduction souris/clavier, 360/768 px, erreurs/focus de l'assistant, navigation GET du dashboard avec/sans JS et Entrée, géométrie/couverture du bouton et événements. Aucun sleep ni clic forcé, aucun POST métier final. Cause racine non démontrée ; aucun correctif produit spéculatif.
- Lecture du code : forms.js ne sélectionne que les formulaires POST. Le GET du dashboard ne reçoit donc pas noValidate de ce script. Cette observation n'explique pas à elle seule l'échec de clic.
- Chrome direct bloqué (setsockopt Operation not permitted) ; tentative du lanceur de diagnostic arrêtée sur socket locale refusée, rapport /tmp/pharmagest-ux-report-ghyjmdhn. Douze cas non exécutés dans le navigateur ; commande hôte et tableau honnête ajoutés à RECETTE_UX. Attendre le rapport avant de conclure sur le lot 1 et poursuivre le lot 2.

- Non-régression réellement exécutée dans la copie : 85 tests Django réussis (158,053 s), check Django sans anomalie, aucune différence de migration, 12 tests JS caisse et 9 tests JS opérations réussis. Syntaxe du diagnostic Node et compilation du lanceur Python valides. Préparation isolée réussie : 45 rendus serveur.
- Commit atomique de test `a83f1df` sur fix/recette-frontend dans la copie isolée. Documentation mise à jour séparément ; bundle local destiné à importer uniquement cette branche, sans déplacement de main, merge ou push. Aucun correctif applicatif déclaré résolu ; attente du rapport lot1.json avant la suite.

## 30 octobre 2026 — Rapport lot 1 du poste utilisateur

- Rapport /tmp/pharmagest-ux-report-426mt8qc lu intégralement pour les douze cas ; capture du KO inspectée. 11 OK / 1 KO. Les quatre passages de l'assistant atteignent Prix avec focus sur LEGEND ; sept navigations du dashboard réussissent.
- KO : souris à 360 px sans JS applicatif ; champs valides, noValidate=false, URL inchangée, focus sur dashboard-end. Anciennes traces sans sonde dans le contexte sans JS : cause non démontrée. Aucun correctif produit, aucun test de régression produit déclaré réussi.
- Diagnostic limité à ce cas et répétable cinq fois, navigation observée sans cookie/header, sonde lecture seule, géométrie et capture du viewport avant clic ; erreurs détaillées affichées dans le terminal. Aucun clic forcé, sleep ni deuxième clic automatique.
- Vérification actuelle : syntaxe Node, compilation Python, diff sans erreur ; nouvelle instrumentation non exécutée dans un navigateur ici. Les 85 tests et 21 tests JS sont ceux du passage précédent, non rejoués pour ce changement d'outillage. Tableau de résultats réels ajouté à RECETTE_UX. Lot 1 toujours en attente de conclusion, pas de passage au lot 2, aucun merge/push.

## 30 octobre 2026 — Lot 2 poursuivi à la demande de l'utilisateur

- Rapport 8d0__y96 : 1 OK et 4 KO sur cinq clics à 360 px sans JS. Cause non démontrée. L'utilisateur autorise le report de ce défaut et le passage à la matrice.
- Mode --matrix et ux_matrix_check.cjs ajoutés : cinq rôles, deux thèmes, quatre largeurs, JS/sans JS, 720 cas prévus ; collecte de tous les résultats et contrôles différés déclarés. Aucun correctif produit.
- Tentative locale bloquée par les sockets, rapport kfbqsr68. Préparation isolée : 45 rendus serveur réussis (9yh2w_nv), syntaxe Node et Python vérifiées. Aucun merge/push.
- Lors de la tâche suivante, découverte d'un écrasement involontaire du journal par le contenu d'avancement : historique restauré depuis la copie QA de la branche, puis événements ultérieurs réintégrés.

## 30 octobre 2026 — Vérification de l'hypothèse wsgiref et métadonnées

- Demande utilisateur : comparer dix essais single à vingt threaded, journaliser les heures et requêtes, ajouter favicon/meta, sans modification de vue/modèle/permission ni push.
- Serveur instrumenté créé, témoin single conservé et ThreadedWSGIServer disponible/par défaut. Même handler et file ; aucune lecture réseau forcée à expirer, fermeture des clients seulement au nettoyage. Traces UTC sans en-tête/cookie/corps persisté.
- Deux tentatives finales exécutées : single à 08:17:48.100 UTC (10 demandés), threaded à 08:17:57.602 UTC (20 demandés), refus de socket avant écoute dans les deux cas. Zéro passage navigateur exécuté et aucune requête HTTP reçue ; rapports n01o0e0c et 01vc845r. Aucun comparatif de succès ni cause racine démontrée.
- Diagnostic : checkValidity, elementFromPoint et trace JSON horodatée des résultats séparés activation/navigation. Les deux commandes exactes et critères de conclusion sont dans RECETTE_UX ; attendre les rapports du poste.
- Ajout favicon SVG et balise, meta theme-color système/manuelle synchronisée. Contrôles : trois tests Python outillage, cinq tests Node thème et 21 tests JS existants ; douze tests Django ciblés puis deux tests métadonnées (SVG servi en 200), check et syntaxe/compilation sans erreur. Suite complète non rejouée ; navigateur/métadonnées visuelles non vérifiés.
- Aucun fichier vue, modèle, service, permission ou migration modifié. Aucun push/merge. Journal historique restauré lors de cette tâche, après écrasement involontaire précédemment détecté.

## 2 novembre 2026 — Comparatif réseau réel et témoin navigateur

- Rapports du poste _0hmnjzp et e8jza826 lus. Single : 10 passages, 1 OK/9 KO ; threaded : 20 passages, 0 OK/20 KO. 85 et 154 HTTP reçus, tous terminés ; aucune connexion acceptée sans en-têtes. Un seul GET de période, en single à 05:27:25.513 UTC. Les 29 KO sont des délais du clic attendant la stabilité avant requête, formulaire valide.
- Ce comparatif ne soutient pas l'hypothèse serveur/préchauffage. Aucun diagnostic produit ni correctif alternatif affirmé sans preuve.
- Versions locales observées : Playwright cache Go 1.50.1, google-chrome 145.0.7632.109, Chromium 133 déclaré par le package ; piste de compatibilité, pas preuve de cause.
- Ajout de ux_browser_probe.cjs et --probe-browser : page synthétique hors Django, JS/sans JS, géométrie/rAF/focus, clic locator et contrôle physique uniquement sur ce témoin, versions/captures/traces sans identifiants. Aucun serveur, aucune préparation de base ou dépendance nouvelle.
- Tentative réelle : Chrome ne démarre pas dans le bac à sable ; rapport wjqmsqcq, cas navigateur non exécutés. Trois tests de journalisation réussis (0,125 s), syntaxe Node, compilation Python et diff valides ; suite complète non rejouée. Attendre le rapport du poste. Aucun push, aucun changement de vue/modèle/service/permission/migration.

## 2 novembre 2026 — Témoin viewport réussi et isolation du défilement

- Rapport m7tpz2it lu : locator.click OK avec/sans JS, bouton fixe dans le viewport, focus reçu ; Chrome 145 et Playwright 1.50.1 réellement utilisés. Aucun Chromium embarqué disponible. rAF de page absent sans JS alors que le clic passe ; aucune cause déduite de l'écart de versions ou des sondes vides.
- Bootstrap local impose scroll-behavior:smooth sous no-preference ; le bouton réel est hors viewport dans plusieurs échecs. Extension du témoin à viewport/offscreen-auto/offscreen-smooth avec/sans JS, remplissage de date préalable dans les deux cas hors écran, coordonnées document et viewport consignées.
- Aucun CSS de l'application modifié ; hypothèse défilement encore non démontrée. Six nouveaux cas à exécuter via --probe-browser. Syntaxe Node et diff vérifiés ; exécution locale du témoin bloquée au lancement Chrome, aucun succès nouveau revendiqué.

## 2 novembre 2026 — Correctif du défilement après témoin contrôlé

- Rapport olrbhn5i lu et captures présentes vérifiées : viewport, offscreen-auto, offscreen-smooth avec/sans JS ; seul offscreen-smooth sans JS est KO, géométrie document fixe. Condition isolée par comparaison ; mécanisme interne navigateur non affirmé.
- Correctif minimal : root scroll-behavior:auto dans app.css, après Bootstrap. Aucun autre composant ni logique métier modifié. Valeur calculée ajoutée au diagnostic.
- Non-régression réelle à exécuter sur le poste : vingt passages dashboard-360-sans-js-mouse ; témoin négatif smooth conservé comme témoin, pas utilisé pour juger le produit corrigé. Résultats après correction non exécutés ici.
- Vérifications après le correctif CSS : 13 tests Django de présentation/métadonnées réussis (23,291 s), check Django sans anomalie, syntaxe Node et diff sans erreur. Ces résultats ne remplacent pas la validation navigateur après correction.

## 2 novembre 2026 — Résolution vérifiée et lancement du lot 2

- Déclaration de résolution corroborée par le rapport dbxll7ue : vingt passages exécutés et réussis, snapshots auto, vingt GET de période dans 174 HTTP. Avant surcharge CSS : zéro réussite sur vingt en threaded ; après : vingt sur vingt. Défaut précis du clic clos pour ce périmètre, sans généraliser à l'ensemble de l'interface.
- Mode --matrix actualisé pour retirer le défaut résolu des reports et conserver l'examen visuel/parcours détaillés comme restant à faire. Statut automatique distinct manual_review_pending.
- Nouvelle tentative locale --matrix bloquée à l'ouverture du socket, rapport wvpnl77f ; aucun cas navigateur exécuté. Syntaxe Node, compilation Python et diff sans erreur. Prochaine action : exécution sur le poste, puis analyse des matrix.json et des captures. Aucun commit/merge/push.

## 2 novembre 2026 — Vérification de la matrice avant checkpoint

- Rapport uwt80wl_ inspecté : administrateur 176, pharmacien 176, caissier 96, stock 144, gestion 128, tous OK ; total 720 avec 45 pages dans chaque combinaison de thème/JS/largeur, 1534 HTTP. Toutes les captures présentes ; empreintes des JSON et table des 720 résultats ajoutées à RECETTE_UX.
- Trois captures examinées : stocks sombre/sans JS/768, formulaire clair/JS/1280, dashboard sombre/JS/1920. Défaut de lisibilité du stock détecté malgré les assertions OK : colonnes trop comprimées. Réutilisation de min-width catalogue dans stock-table, largeur minimale des deux premières colonnes ; cartes <=600 px préservées.
- Après retouche, test de rendu des pages principales réussi (2,044 s). Recette ciblée stock et nouvelle inspection à faire ; la matrice 720 ne prétend pas tester les fichiers après cette dernière retouche. Impression/PDF, lecteur d'écran, examen visuel exhaustif et mesure caisse restent ouverts.
- .publication, .venv et db.sqlite3 ignorés et non suivis ; fichiers métier protégés sans diff. Aucun commit, merge ou push.
- Contrôles réexécutés pour le checkpoint : 87 tests Django réussis (157,887 s), trois tests Python d'outillage réussis (0,175 s), 12 + 9 + 5 = 26 tests JS réussis, check Django et absence de changement de migration vérifiés. Le contrôle complet et le rendu serveur ne prouvent pas l'aspect de la nouvelle retouche stocks : validation navigateur ciblée toujours nécessaire.

## 2 novembre 2026 — Contrôle stocks et intégration autorisée

Rapport 4_0pr859 vérifié : 144 cas du rôle stock, tous OK après retouche du tableau. Cette réussite automatique ne remplace pas l'examen visuel exhaustif. L'utilisateur autorise maintenant le commit dans fix/recette-frontend puis la fusion dans main, sans demande de push. Tentative git add refusée : .git/index.lock en lecture seule. Aucun commit ni fusion effectué dans le dépôt actif par l'agent ; commandes à exécuter dans le terminal utilisateur.

## 2 novembre 2026 — Reprise du lot 3 après fusion

- Git vérifié : main propre à 3b28d08, référence locale origin/main identique ; fusion frontend confirmée. Les commandes historiques précédemment fournies ont donc été intégrées dans le dépôt utilisateur. Aucun accès réseau ni push par l’agent.
- Trois captures examinées : stock sombre sans JS 768 récent (noms lisibles), caisse sombre JS 360, achat partiel sombre JS 1280. Pas de validation exhaustive ni d’impression déduite de ces images.
- Option --matrix --presentation et module de mesure des contrastes/impression ajoutés, avec cinq tests mathématiques réussis. Inventaire documenté : 39 tokens et quatre effets RGB légitimes, sur 43 occurrences. Aucun changement de fichier applicatif.
- Tentative navigateur fkt1jp4z : refus de socket, zéro requête, aucun rôle exécuté. Commande poste et exclusions dans RECETTE_PRESENTATION.md. Check Django, syntaxe et diff vérifiés ; suite Django complète non rejouée pour ces outils/docs. Aucun commit/merge/push.

## 2 novembre 2026 — Rapport présentation et commit demandé

- Rapport hôte kqi1nqyl lu : 176/176 pages administrateur OK, 11 536 ratios au repos tous >=4,5 (minimum 5,4348), huit contrôles désactivés exclus, 342 HTTP terminés, 176 captures et 12 PDF/captures présents.
- Trois PDF sombres JS convertis et inspectés (vente brouillon, achat partiel, page de liens rapports), chacun une page. Lisibilité/fond clair confirmés sur ces exemples ; colonnes Actions vides et liens imprimés à améliorer. Pas de preuve des rapports métier ReportLab ni multipage.
- Cinq tests JS relancés avec succès ; check Django, syntaxe Node, compilation Python et diff vérifiés. Pas de nouveau passage complet Django. Bilan, matrice agrégée et empreinte enregistrés dans RECETTE_PRESENTATION.md.
- Utilisateur autorise un commit dans une branche. git switch -c test/recette-presentation échoue sur écriture des refs ; aucun contournement, commit, merge ou push. Commandes finales destinées au terminal utilisateur.

## 2 novembre 2026 — Retouches ciblées avant recette des cinq rôles

- Commit bbe1005 confirmé sur test/recette-presentation, dossier initialement propre. Réutilisation de no-print dans les fiches vente/achat et la page rapports pour les défauts papier prouvés par kqi1nqyl ; assertions de non-régression ajoutées à la recette navigateur.
- 11 tests PresentationTests réussis (20,248 s), cinq tests JS de contraste réussis, syntaxe Node, check Django et diff valides. Fichiers backend protégés sans diff.
- Tentative --matrix --presentation --role administrateur bloquée avant serveur, rapport 2obe37jh, zéro requête. Validation après correction non exécutée ; commande poste pour les cinq rôles : --matrix --presentation. Aucun nouveau commit/merge/push.

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
