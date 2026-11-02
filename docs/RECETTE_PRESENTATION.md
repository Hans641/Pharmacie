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
