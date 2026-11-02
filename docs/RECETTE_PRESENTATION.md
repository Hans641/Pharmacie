# Lot 3 — Contrastes rendus et impression HTML

Reprise du 2 novembre 2026 sur `main` / `3b28d08`, dossier propre avant travail ; `origin/main` local identique, sans interrogation réseau. Fusion confirmée par Git, contrairement à la dernière entrée historique de mémoire.

## État réel

| Contrôle | Résultat | Preuve / limite |
|---|---|---|
| Stocks sombre, sans JS, 768 px après correction | Inspection visuelle : noms lisibles, défilement interne conservé | `/tmp/pharmagest-ux-report-4_0pr859/stock/dark-sans-js-768-_stocks_.png` |
| Caisse sombre, JS, 360 px | Capture examinée ; panier, total, ordonnance et paiement présents | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-360-_ventes_7_.png` ; ne valide ni actions ni contrastes ni zoom |
| Achat partiel sombre, JS, 1280 px | Capture examinée ; colonnes et montants lisibles | `/tmp/pharmagest-ux-report-4_0pr859/stock/dark-js-1280-_achats_2_.png` ; impression non exécutée |
| Mesures de contraste DOM et impression navigateur | **Non exécuté** | Tentative `/tmp/pharmagest-ux-report-fkt1jp4z/summary.json` : socket refusée, zéro requête et aucun rôle exécuté |
| Calculs de luminance et composition alpha | 5 tests réussis | `node tools/ux_presentation.test.cjs` ; tests de calcul, pas de rendu |

## Lancer sur le poste

```bash
# Première passe, administrateur : 176 pages avec assertions communes + contrastes
.venv/bin/python tools/run_ux_review.py --matrix --presentation --role administrateur
# Puis les cinq rôles : 720 pages
.venv/bin/python tools/run_ux_review.py --matrix --presentation
```

Fournir le chemin du rapport annoncé, même en cas de KO. Ne pas relancer immédiatement un échec : examiner `administrateur.log` et `administrateur/matrix.json`. Aucun POST commercial exécuté par le navigateur ; base/médias de recette isolés comme précédemment. Les dates et les cookies de session ne sont pas archivés par cet ajout ; les captures portent des données fictives.

Chaque ligne de `matrix.json` garde son rôle, page, largeur, JS, thème et capture. `presentation.pairs` contient les couleurs calculées puis composées, le ratio non arrondi, la taille/graisse et le verdict 4,5:1. `presentation.skipped` explique les éléments nécessitant une inspection distincte : transparence globale, filtres, images/dégradés, désactivation, couleurs non reconnues. Ces exclusions ne sont pas des réussites. Les placeholders, pseudo-éléments, superpositions, contrôles natifs ouverts et états interactifs restent à examiner. Les fonds simples des ancêtres sont composés sur un canevas blanc ; ce calcul ne prétend pas déterminer les pixels derrière un élément superposé.

À 1280 px, les détails de vente, d’achat et les rapports produisent aussi `*-print.png` et `*-print.pdf`, dans les deux thèmes et avec/sans JS. Vérification du fond blanc, schéma clair, disparition des contrôles, répétition CSS des en-têtes, absence de débordement et règle de non-coupure des lignes. Une règle CSS ne prouve pas le découpage effectif sur plusieurs feuilles. Les PDF sont des impressions Chromium du HTML, indépendantes des documents ReportLab du lot 5. Un PDF créé n’est pas marqué comme inspecté visuellement.

```bash
# Après réception d’un PDF de recette : chemin exact à remplacer
pdftoppm -png -r 120 /chemin/vers/document-print.pdf /tmp/pharmagest-print-page
pdftotext -layout /chemin/vers/document-print.pdf -
```

## Couleurs littérales : inventaire de source

Classification au 2 novembre : **43 occurrences**, dont **39 tokens** (38 hexadécimales et une ombre RGB) et **4 effets légitimes RGB**. Aucun littéral de texte/fond de composant hors token identifié dans ces deux fichiers. Ce constat de source ne garantit pas les contrastes rendus ; aucun correctif CSS n’est justifié sans défaut démontré.

| Fichier:ligne | Valeur | Classe | Justification |
|---|---|---|---|
| `static/css/app.css:9` | `#126749` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:10` | `#0c4935` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:11` | `#fff` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:12` | `#738c7c` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:13` | `#7f9688` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:14` | `#344f40` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:15` | `#e1efe6` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:16` | `#294b37` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:17` | `#324e3d` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:18` | `#5e7065` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:19` | `#eaf0ec` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:20` | `#344c3d` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:21` | `#2b4636` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:22` | `#f3f8f4` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:23` | `#9bb6a5` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:24` | `#aa792a` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:25` | `#bd6863` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:26` | `#6d9a7b` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:27` | `#e8eee9` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:28` | `#9bad9f` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:29` | `#c1d6e5` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:30` | `#126749` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:31` | `#0c4935` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:32` | `#182d25` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:33` | `#52675d` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:34` | `#f4f7f5` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:35` | `#fff` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:36` | `#edf4ef` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:37` | `#c7d5cd` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:38` | `#175d3b` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:39` | `#e6f4eb` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:40` | `#784500` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:41` | `#fff2d9` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:42` | `#a12727` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:43` | `#fff0ef` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:44` | `#18567e` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:45` | `#e9f3fb` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:46` | `#1759bd` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:60` | `rgb(18 49 32 / 8%)` | token | Palette ou ombre définie comme variable. |
| `static/css/app.css:307` | `rgb(12 31 21 / 55%)` | légitime | Ombre ou voile translucide : effet de profondeur, sans couleur de texte. Rendu/superposition à contrôler. |
| `static/css/app.css:333` | `rgb(12 31 21 / 50%)` | légitime | Ombre ou voile translucide : effet de profondeur, sans couleur de texte. Rendu/superposition à contrôler. |
| `static/css/app.css:357` | `rgb(18 49 32 / 6%)` | légitime | Ombre ou voile translucide : effet de profondeur, sans couleur de texte. Rendu/superposition à contrôler. |
| `static/css/experience.css:100` | `rgb(18 49 32 / 5%)` | légitime | Ombre ou voile translucide : effet de profondeur, sans couleur de texte. Rendu/superposition à contrôler. |

## Recette manuelle restante du lot 3

- Connexion et réinitialisation, pages 403/404/500 : non couvertes par les 45 routes de la matrice ; à examiner séparément sur données de test.
- Pour chaque famille : hover, focus, erreur, désactivation, badges, tableaux, dialogue, date/select/checkbox natifs et défilement. La matrice mesure les textes au repos seulement.
- Zoom navigateur réel 200 % et texte agrandi : caisse et formulaire, à 360/768/1280/1920 px ; ne pas assimiler une réduction de viewport à un test de zoom.
- Aperçu d’impression : reçu/caisse, achat et rapports, fond clair en partant du thème sombre, montants, accents et tableaux sur plusieurs feuilles ; médias fictifs uniquement.
- Lecteur d’écran et ordre complet de tabulation : toujours non exécutés.

La prochaine décision dépend des rapports réels : corriger uniquement les défauts mesurés, puis relancer les cas affectés. Les lots chronométrage et PDF ReportLab restent distincts.

## 2 novembre 2026 — Rapport hôte kqi1nqyl vérifié

Commande exécutée par l’utilisateur : `--matrix --presentation --role administrateur`. Rapport lu et analysé : **176/176 OK**, aucun KO, 176 captures présentes, 342 requêtes reçues et terminées. **11 536 mesures de contraste au repos**, toutes >=4,5:1, minimum **5,4348:1** ; huit exclusions de contrôles désactivés. Ces mesures répétées ne sont pas 11 536 composants distincts et ne couvrent ni tous les états ni tous les rôles. Les 12 impressions PDF et leurs captures sont présentes et passent les assertions de structure. La caisse imprimée est un brouillon, pas un reçu encaissé.

Source : `/tmp/pharmagest-ux-report-kqi1nqyl/administrateur/matrix.json`.
SHA-256 : `4b49baa5efb6c629007898548b6e952d4f1ef4022a4038e91ecbb97456eeb0eb`.

| Rôle | Largeur | JS | Thème | Pages OK / exécutées | Preuve |
|---|---:|---|---|---:|---|
| administrateur | 360 | sans | dark | 11/11 | `administrateur/matrix.json` et captures `dark-sans-js-360-*.png` |
| administrateur | 360 | sans | light | 11/11 | `administrateur/matrix.json` et captures `light-sans-js-360-*.png` |
| administrateur | 360 | avec | dark | 11/11 | `administrateur/matrix.json` et captures `dark-js-360-*.png` |
| administrateur | 360 | avec | light | 11/11 | `administrateur/matrix.json` et captures `light-js-360-*.png` |
| administrateur | 768 | sans | dark | 11/11 | `administrateur/matrix.json` et captures `dark-sans-js-768-*.png` |
| administrateur | 768 | sans | light | 11/11 | `administrateur/matrix.json` et captures `light-sans-js-768-*.png` |
| administrateur | 768 | avec | dark | 11/11 | `administrateur/matrix.json` et captures `dark-js-768-*.png` |
| administrateur | 768 | avec | light | 11/11 | `administrateur/matrix.json` et captures `light-js-768-*.png` |
| administrateur | 1280 | sans | dark | 11/11 | `administrateur/matrix.json` et captures `dark-sans-js-1280-*.png` |
| administrateur | 1280 | sans | light | 11/11 | `administrateur/matrix.json` et captures `light-sans-js-1280-*.png` |
| administrateur | 1280 | avec | dark | 11/11 | `administrateur/matrix.json` et captures `dark-js-1280-*.png` |
| administrateur | 1280 | avec | light | 11/11 | `administrateur/matrix.json` et captures `light-js-1280-*.png` |
| administrateur | 1920 | sans | dark | 11/11 | `administrateur/matrix.json` et captures `dark-sans-js-1920-*.png` |
| administrateur | 1920 | sans | light | 11/11 | `administrateur/matrix.json` et captures `light-sans-js-1920-*.png` |
| administrateur | 1920 | avec | dark | 11/11 | `administrateur/matrix.json` et captures `dark-js-1920-*.png` |
| administrateur | 1920 | avec | light | 11/11 | `administrateur/matrix.json` et captures `light-js-1920-*.png` |

Trois PDF (sombre, JS, 1280 px) convertis avec `pdftoppm`, texte extrait avec `pdftotext`, puis images examinées :

| Document HTML imprimé | Pages | Résultat visuel de cet échantillon | Image inspectée |
|---|---:|---|---|
| Vente brouillon VEN-000005 | 1 | Lisible, montants à droite et ariary français, fond clair ; colonne Actions vide et double rappel du total conservés | `/tmp/pharmagest-print-review-kqi1nqyl/dark-js-1280-_ventes_5_-print.png` |
| Achat partiel ACH-000002 | 1 | Lisible, montants/accents corrects ; colonne Actions vide et lien Bon de réception PDF conservés | `/tmp/pharmagest-print-review-kqi1nqyl/dark-js-1280-_achats_2_-print.png` |
| Page Rapports & documents | 1 | Page de liens lisible, pas le contenu des rapports ; liens Télécharger le PDF encore imprimés | `/tmp/pharmagest-print-review-kqi1nqyl/dark-js-1280-_rapports_-print.png` |

Les liens d’action et colonnes vides sont des améliorations de présentation restantes ; les assertions de contrôles masqués ne vérifient pas tous les liens. Aucun défaut de calcul ni de permission déduit de ces observations. Multipage, reçu validé, rapports métier PDF/ReportLab, quatre autres rôles, zoom et états interactifs restent non vérifiés dans ce passage. Ce checkpoint n’achève pas le lot 3.

Contrôles réexécutés : cinq tests JS de calcul réussis, syntaxe Node, compilation Python, `manage.py check` et `git diff --check` sans anomalie. Suite Django complète non rejouée pour ces seuls outils/documents.

Commit autorisé dans une branche dédiée, sans merge ni push. Tentative `git switch -c test/recette-presentation` refusée par les droits d’écriture de `.git` ; aucun commit ni création de branche effectué par l’agent. Les changements restent dans le dossier de travail de main pour être enregistrés depuis le terminal utilisateur. Les preuves `/tmp` sont locales et peuvent disparaître au redémarrage ; le bilan et l’empreinte sont conservés dans ce document.

## 2 novembre 2026 — Retouches d’impression après checkpoint

Commit précédent confirmé par Git : `bbe1005` sur `test/recette-presentation`, dossier propre au début de la reprise. Aucun nouveau commit, merge ou push effectué.

Cause démontrée par les trois images du rapport kqi1nqyl : masquer les boutons ne masque ni la colonne Actions ni les invites de téléchargement en liens/strong. Réutilisation de `no-print`, déjà géré par la feuille print locale ; aucune permission, logique métier ou règle écran changée intentionnellement.

| Fichier | Avant | Après |
|---|---|---|
| `templates/pharmacy/sale_detail.html` | Colonne Actions vide sur papier | En-tête et cellules marqués no-print |
| `templates/pharmacy/purchase_detail.html` | Colonne Actions et lien de réception PDF imprimés | Masqués sur papier ; total dans sa colonne avec cellule d’action séparée, masquée à l’impression |
| `templates/pharmacy/reports.html` | Invite Télécharger le PDF sur papier | Invite masquée, titres et descriptions conservés |
| `tools/ux_presentation.cjs`, `tools/ux_matrix_check.cjs` | Contrôle des boutons/champs seulement | Régression : compter les en-têtes Actions et invites PDF encore visibles ; exiger zéro |

Contrôles réels : **11 tests PresentationTests réussis (20,248 s)**, **5 tests JS de calcul réussis**, syntaxe Node, check Django et diff sans anomalie. Le rendu serveur ne prouve pas l’impression. Nouvelle tentative navigateur : `/tmp/pharmagest-ux-report-2obe37jh`, socket refusée, zéro requête, **validation navigateur après correction non exécutée**. Les 176 succès du rapport précédent concernent les templates avant ces retouches.

Commande suivante sur le poste, cinq rôles et nouvelle présentation :

```bash
.venv/bin/python tools/run_ux_review.py --matrix --presentation
```

Attendre ce rapport et inspecter les PDF actualisés avant de clore ces défauts. Les champs/états non couverts, le zoom, le multipage et ReportLab restent des vérifications distinctes.

## 2 novembre 2026 — Recette des cinq rôles après retouches

Rapport hôte `5wjmy_iw` analysé : **720/720 cas OK**, 720 captures présentes, **1 534 requêtes reçues et terminées**, **47 038 mesures de contraste au repos >=4,5:1**, minimum global **5,4348:1**. Vingt-quatre exclusions de contrôles désactivés, aucune exclusion présentée comme réussite. La révision Git de base du rapport est `bbe1005` ; les retouches non commitées du dossier de travail étaient utilisées lors de ce passage.

Chaque rôle couvre les quatre largeurs (360/768/1280/1920), les deux thèmes et JS/sans JS. Le détail page par page avec captures et mesures se trouve dans les fichiers ci-dessous, sous `/tmp/pharmagest-ux-report-5wjmy_iw/`.

| Rôle | Cas OK / exécutés | Mesures de contraste | Minimum | PDF HTML | Preuve |
|---|---:|---:|---:|---:|---|
| administrateur | 176/176 | 11536 | 5.4348:1 | 12 | `administrateur/matrix.json` |
| caissier | 96/96 | 7558 | 5.4831:1 | 8 | `caissier/matrix.json` |
| gestion | 128/128 | 8654 | 5.4831:1 | 12 | `gestion/matrix.json` |
| pharmacien | 176/176 | 11378 | 5.4348:1 | 12 | `pharmacien/matrix.json` |
| stock | 144/144 | 7912 | 5.4348:1 | 8 | `stock/matrix.json` |

### Impression : vérification après correction

Les **52 PDF et leurs captures** sont présents ; `pdfinfo` confirme une page par document. Extraction du texte des 52 PDF avec `pdftotext` : aucune occurrence « Actions », « Télécharger le PDF » ou « Bon de réception PDF ». Les assertions d’impression confirment fond blanc/schéma clair, contrôles masqués, absence de débordement et règles d’en-tête/non-coupure des lignes pour les tableaux présents.

Trois PDF administrateur sombre/JS ont été convertis avec `pdftoppm` et leurs images inspectées : vente brouillon VEN-000005, achat partiel ACH-000002 et page Rapports & documents. Résultat : colonnes et invites retirées, montants alignés et libellés lisibles. Images :

- `/tmp/pharmagest-print-review-5wjmy_iw/dark-js-1280-_ventes_5_-print.png`
- `/tmp/pharmagest-print-review-5wjmy_iw/dark-js-1280-_achats_2_-print.png`
- `/tmp/pharmagest-print-review-5wjmy_iw/dark-js-1280-_rapports_-print.png`

Les défauts précis d’impression sont résolus dans ce périmètre. La vente est un brouillon ; la page Rapports est un index, pas les documents métier. Le rappel du total dans Encaissement est conservé. Aucun succès de multipage, reçu encaissé ou PDF ReportLab déduit de ces résultats. États interactifs exhaustifs, pages d’authentification/erreur, zoom réel 200 %, lecteur d’écran et chronométrage restent ouverts. Aucun nouveau test Django exécuté lors de cette analyse documentaire ; les 11 tests ciblés précédents concernaient déjà les retouches testées ici. Pas de commit/merge/push pendant l’analyse.

### Empreintes des preuves

- `administrateur/matrix.json` : `f35cf6dd1f0ca58feff1add4717a3769ac3d7193c486c8783de0cae6e7428396`
- `caissier/matrix.json` : `cb74c37deb4631770320b5a4aaac9594b295e90351ef8f413e4a50d57b8796d9`
- `gestion/matrix.json` : `bf3e52c21d093275bb3c2636b8cbe0e2bc84187c7e2225ddf64f2b354ac7bb89`
- `pharmacien/matrix.json` : `e280f441eb38a32663ec40e340f20d6ae2407e11f977e0edd269b23ae1799ab5`
- `stock/matrix.json` : `5ebdbaa61fcbd3e0bf3376682c62500b8a865113fc627241e85b84fdd9d513e6`

## 2 novembre 2026 — Complément authentification et accessibilité

Fusion précédente confirmée sur main à `9bf65ad`, dossier initialement propre. Nouveau mode de recette :

```bash
.venv/bin/python tools/run_ux_review.py --accessibility
```

112 cas prévus : sept pages × quatre largeurs × deux thèmes × JS/sans JS. Pages HTTP anonymes : connexion, demande de réinitialisation, confirmation de demande et fin de réinitialisation. Les trois autres cas sont les templates 403/404/500 rendus isolément par Django avec un utilisateur anonyme, chargés par Playwright sur l’origine locale ; **ils ne prouvent pas le comportement des handlers HTTP ni le traitement réel d’une erreur**. Aucun POST n’est autorisé dans ces contextes navigateur. Les erreurs testées sont locales, avant soumission, sans connexion réelle ni envoi de courriel.

Assertions : langue/titre H1, schéma rendu, débordement, focus visible et transition réduite du premier bouton ; affichage/masquage du mot de passe au clavier et aria-pressed ; erreur inline/focus après formulaire vide avec JS ; contrastes des textes mesurables après ces interactions. Les états non mesurables restent consignés par le module de contrastes. Captures et verdicts par cas dans `administrateur/accessibility.json`, initialisés non exécutés et enregistrés progressivement.

Tentative locale réellement exécutée : `/tmp/pharmagest-ux-report-ru1ddq2f`, socket refusée avant serveur ; zéro requête et **aucun cas navigateur exécuté**. Rendus isolés préparés avant ce refus. Syntaxe Node/Python, check Django, diff et cinq tests de calcul de contrastes vérifiés ; suite Django complète non rejouée. Aucun composant, modèle, vue, service ou permission modifié. Aucun commit/merge/push.

### Vérifications manuelles encore nécessaires

- Sur une base fictive, ouvrir caisse et formulaire aux quatre largeurs, régler le zoom du navigateur à 200 % via son menu et relever le zoom réellement affiché ; faire séparément un passage avec texte agrandi seul. Vérifier labels, erreurs, boutons et total accessibles sans chevauchement. Une simulation de viewport ou un facteur de résolution ne prouve pas le zoom.
- Parcourir au clavier tous les champs et actions, dialogue compris ; vérifier Échap, retour du focus et absence de soumission en annulant. Ne jamais encaisser ou réceptionner sur la base active.
- Examiner les états natifs ouverts (select/date), désactivation, erreurs serveur, réinitialisation avec lien valide/invalide et lecteur d’écran. Ces parcours ne sont pas couverts par le nouveau mode.

Attendre le rapport hôte avant de conclure à la réussite des nouveaux cas. La recette ne constitue pas une certification WCAG.

## 2 novembre 2026 — Rapport accessibilité e5mzo9ly : arrêt commun au focus

Rapport lu : 112/112 KO, tous à l’assertion « Focus visible », outline calculé 0px/none sur le premier bouton. Les assertions suivantes (survol, mot de passe, validation locale et contrastes) n’ont pas été atteintes. Ne pas assimiler ces résultats à 112 défauts indépendants.

Cause de cascade confirmée dans Bootstrap local : `.btn:focus-visible` impose `outline:0`, plus spécifique que la règle générique `:focus-visible` de app.css. Un box-shadow Bootstrap peut exister : le rapport précédent ne le mesurait pas, donc aucune conclusion d’absence totale d’indicateur. Correction : règle `.btn:focus-visible` de même spécificité après Bootstrap, contour de 3px avec le token focus. Script corrigé pour activer explicitement la modalité clavier, enregistrer activeElement/:focus-visible/box-shadow et afficher les erreurs dans le terminal. Aucune suppression de l’assertion ni changement métier.

Syntaxe Node, check Django et diff vérifiés. La validation navigateur après correction reste à obtenir ; commande : `.venv/bin/python tools/run_ux_review.py --accessibility`. Aucun succès après correction revendiqué, aucun commit/merge/push.

## 2 novembre 2026 — Rapport faugqo54 : 104 OK / 8 KO

Rapport accessibility.json lu : 104 réussites et huit échecs, exclusivement connexion sans JS aux quatre largeurs et deux thèmes. Dans les huit cas, active=false et :focus-visible=false. Le sélecteur `main .btn` choisissait le bouton Afficher du mot de passe, présent dans le template mais hidden sans JS ; le template includes/field.html et le script app.js confirment ce repli intentionnel. Le script essayait donc de focaliser un contrôle masqué. Aucun défaut produit déduit de ces huit échecs.

Correction d’outillage uniquement : `main .btn:visible`, ajout du libellé du contrôle mesuré au diagnostic. L’assertion exigeant que le bouton Afficher soit masqué sans JS est conservée, ainsi que tous les contrôles de focus. Les 104 cas réussis confirment le contour de focus de 3px dans le périmètre testé ; les assertions après l’échec des huit cas n’ont pas été exécutées.

Syntaxe Node et git diff --check vérifiés. Validation après cette dernière correction encore attendue : `.venv/bin/python tools/run_ux_review.py --accessibility`. Aucun nouveau test Django complet, commit, merge ou push. Ne pas transformer 104 réussites et huit corrections attendues en 112 réussites mesurées.

## 2 novembre 2026 — Rapport f2gyt6jp : 112 cas réussis

Rapport hôte lu : **112/112 OK**, 112 captures présentes et 1 064 requêtes reçues/terminées. Dans les 112 cas, le contrôle testé est actif avec contour de focus de 3px. Les 1 024 mesures de contraste après interactions sont OK (minimum 5,6320:1). Seize cas JS vérifient une erreur locale et le focus sur le champ invalide. Afficher/masquer et son repli sans JS passent dans les cas de connexion. Ce ne sont pas des tests d’envoi de courriel ni de connexion réelle.

| Page | Cas OK / exécutés | Nature de la preuve |
|---|---:|---|
| `/comptes/login/` | 16/16 | Page HTTP anonyme |
| `/comptes/password_reset/` | 16/16 | Page HTTP anonyme |
| `/comptes/password_reset/done/` | 16/16 | Page HTTP anonyme |
| `/comptes/reset/done/` | 16/16 | Page HTTP anonyme |
| `template-403` | 16/16 | Rendu isolé du template |
| `template-404` | 16/16 | Rendu isolé du template |
| `template-500` | 16/16 | Rendu isolé du template |

Deux captures sombres inspectées : connexion sans JS à 360 px (bouton Se connecter focalisé, Afficher absent) et template 500 avec JS à 768 px (retour accueil focalisé), lisibles sans débordement visible. Fichiers sous `/tmp/pharmagest-ux-report-f2gyt6jp/administrateur/` : `dark-sans-js-360-_comptes_login_.png`, `dark-js-768-template_500.png`.

Le défaut de contour et le faux échec du bouton masqué sont clos dans ce périmètre. Limites maintenues : zoom navigateur réel 200 %, texte agrandi, lecteur d’écran/ordre complet, dialogues métier/contrôles natifs ouverts, handlers HTTP réels 403/404/500 et liens de réinitialisation valides/invalides. Le lot 3 n’est pas déclaré intégralement terminé. Aucun nouveau test applicatif, commit, merge ou push lors de cette analyse.

Preuve : `/tmp/pharmagest-ux-report-f2gyt6jp/administrateur/accessibility.json` ; SHA-256 : `668b70600a7edb1bf0f5c8b8e5ac4d637fcc12d5bb118a4a7959749c0ccb3cad`.

Prochaine recette humaine : [RECETTE_ZOOM_CLAVIER.md](RECETTE_ZOOM_CLAVIER.md), avec serveur fictif interactif `tools/run_manual_review.py`. Protocole préparé, résultats non exécutés.
