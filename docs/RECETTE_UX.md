# Recette UX, accessibilité et non-régression

## Vérifications historiques de la première refonte

- **56 tests Django réussis**, dont les 45 existants et 11 contrats de présentation supplémentaires.
- `manage.py check` : aucune anomalie.
- `makemigrations --check --dry-run` : aucun changement de modèle.
- `node --check static/js/app.js` et `node --check tools/ux_browser_check.cjs` : syntaxe valide.
- Empreintes SHA-256 identiques avant/après pour modèles, vues, services, formulaires Python et migration initiale.
- Contrastes calculés des principaux textes et couleurs sémantiques : résultats dans `REFONTE_UI.md`.
- Aucune ressource HTTP distante référencée par les templates, hors l’URI de namespace SVG qui n’est pas un téléchargement.

**Non exécuté :** recette réelle de Chromium, captures aux quatre largeurs, essais au lecteur d’écran et chronométrage de vente. Le navigateur échoue au démarrage dans l’environnement restreint (`Operation not permitted`). La suite Django vérifie le HTML et les droits, pas la géométrie, le rendu CSS ou l’exécution du JavaScript. Aucune conformité WCAG complète n’est revendiquée.

Les cases suivantes constituent un plan à exécuter ; elles ne sont pas précochées.

## Lancement autonome sur données isolées — 30 octobre 2026

Depuis la racine du projet :

```bash
.venv/bin/python tools/run_ux_review.py
```

Le lanceur crée une base SQLite neuve et des médias temporaires, applique les migrations dans cette base uniquement, prépare cinq comptes et démarre son propre serveur sur un port local libre. Il ignore le `DATABASE_PATH` hérité. Les comptes, leur mot de passe aléatoire et la base temporaire ne sont pas conservés après la fin du processus. Les journaux du serveur sont désactivés ; la sortie du seed affichant normalement un mot de passe reste en mémoire.

Les données comprennent : stock faible, lot bloqué, lot épuisé, lot périmé, péremption proche, médicament et identité longs, commande partiellement reçue, vente validée et paniers fictifs avec ordonnance requise. Les services métier sont utilisés pour préparer les réceptions, inventaires et paniers. Le script navigateur ne soumet pas les opérations métier.

Un dossier neuf `/tmp/pharmagest-ux-report-…` conserve `summary.json`, les journaux par rôle et les captures. Il est annoncé à la fin, même en cas d'échec. La base temporaire est nettoyée sur succès ou erreur gérée ; après une interruption brutale, ne jamais utiliser ses éventuels restes comme base de travail.

Options :

```bash
# Vérifier les données et les rendus serveur, sans navigateur ni serveur réseau
.venv/bin/python tools/run_ux_review.py --prepare-only
# Limiter la recette navigateur à un rôle
.venv/bin/python tools/run_ux_review.py --role caissier
# Choisir un dossier de résultats neuf
.venv/bin/python tools/run_ux_review.py --output /tmp/recette-pharmagest-session
```

Prérequis navigateur : Node, Playwright et Chrome/Chromium. Le lanceur réutilise `PLAYWRIGHT_MODULE_PATH`, une installation Node locale ou le package Playwright du cache Go s'il existe. Il détecte `google-chrome` installé ; aucun téléchargement automatique. Si Playwright manque :

```bash
npm install --prefix /tmp/pharmagest-browser playwright
PLAYWRIGHT_MODULE_PATH=/tmp/pharmagest-browser/node_modules/playwright CHROME_PATH=/usr/bin/google-chrome .venv/bin/python tools/run_ux_review.py
```

Adapter `CHROME_PATH` au navigateur installé. Une erreur de prérequis ou de lancement ne signifie pas que l'interface a passé la recette. Les nouvelles assertions navigateur doivent encore être exécutées sur la machine hôte.

### Résultats réellement observés dans l'environnement de l'agent

- Préparation isolée : **45 rendus serveur réussis pour les cinq rôles**. Un chemin `DATABASE_PATH` hérité pointant vers une sentinelle est ignoré ; sentinelle inchangée. Empreintes de la base active et des médias identiques avant/après ce contrôle.
- Chrome direct : échec `setsockopt: Operation not permitted`, avant rendu.
- Lanceur en mode navigateur : échec à l'ouverture du serveur local (`Operation not permitted`). Rapport d'échec produit ; aucun contrôle navigateur réussi déduit de cette tentative.
- Le script prévoit désormais les captures et débordements aux quatre largeurs avec et sans JS, le lien d'évitement au clavier, la boucle Tab/Maj+Tab du tiroir et les captures de menu ouvert. En cas de défaut après lancement, `echec.png` et `echec.json` complètent les résultats partiels.

Un statut `preparation_ok` valide seulement les données et les réponses serveur. `automated_checks_ok` indique que les assertions navigateur ont passé ; l'examen visuel des captures, le lecteur d'écran, les contrastes complets, le zoom et le chronométrage restent manuels. Aucune certification WCAG n'est déduite de ces statuts.

## Préparation

Utiliser une **base fictive dédiée**. Créer au moins un compte pour chacun des cinq rôles, puis un compte cumulant caissier et gestionnaire de stock. Prévoir : médicament sans lot, stock faible, lots valides distincts, lot à moins de 90 jours, lot périmé, lot bloqué, commande partiellement reçue, vente validée et vente en brouillon.

Le compte de démonstration est administrateur et ne suffit pas pour vérifier la séparation des rôles. Exécuter le parcours avec les comptes dédiés, puis tenter les URL correspondantes avec les rôles non autorisés.

Lancer normalement :

```bash
source .venv/bin/activate
python manage.py runserver
```

## Matrice de tailles

Exécuter les tests communs et les parcours principaux à **360, 768, 1280 et 1920 px**, à zoom 100 %, puis contrôler le reflow à zoom 200 % et 400 %.

| Largeur | Points spécifiques |
|---|---|
| 360 px | Aucun débordement de page ; listes en cartes ; filtres empilés ; actions de formulaire accessibles ; résumé de caisse lisible |
| 768 px | Tiroir mobile ; focus et fermeture ; caisse sur une colonne ; tableaux encore lisibles dans leur conteneur |
| 1280 px | Menu fixe ; caisse en deux colonnes ; total et contrôles d’encaissement visibles ; tableaux contenus |
| 1920 px | Largeur de lecture limitée ; absence de blancs excessifs ; quatre KPI lisibles ; caisse et tableaux équilibrés |

Sur mobile, les tableaux longs deviennent des cartes à 600 px et moins. À 768 px, un défilement interne de tableau reste possible pour préserver la comparaison des colonnes ; la page entière ne doit pas déborder.

## Checklist commune

### Navigation et clavier

- [ ] Premier Tab : lien « Aller au contenu » visible, puis activation vers le contenu.
- [ ] Focus visible partout, ordre logique, aucun piège de focus hors dialog/tiroir.
- [ ] Menu actif sur listes, fiches, création et modification de la même famille.
- [ ] Tiroir : ouverture, Tab et Maj+Tab contenus, fermeture avec Échap, retour du focus au bouton Menu.
- [ ] L’arrière-plan du tiroir ouvert est inerte, puis redevient utilisable à la fermeture.
- [ ] Menus de compte et d’actions utilisables sans souris.
- [ ] Lecture des titres, repères, tableaux/cartes, états et erreurs avec NVDA ou VoiceOver.
- [ ] Cibles de 44 × 44 px ou libellé associé équivalent, sans chevauchement.

### Lisibilité et accessibilité

- [ ] Corps de texte 16 px et texte secondaire 14 px minimum.
- [ ] État compréhensible sans couleur : texte « Bloqué », « Périmé », « Sous 90 jours », etc.
- [ ] Contrastes vérifiés pour normal, survol, focus et erreurs sur les fonds réellement affichés.
- [ ] Quantités et prix alignés, `15 000,00 Ar` partout dans l’interface HTML.
- [ ] Nom de médicament long, nom d’utilisateur long et grands montants sans débordement.
- [ ] Zoom et grande taille de police système sans perte d’action ou de donnée.
- [ ] Réduction des animations respectée si le système la demande.

### Formulaires

- [ ] Libellés, champs obligatoires, aides et erreurs annoncés ensemble.
- [ ] Envoi invalide : valeurs conservées, résumé d’erreurs accessible, liens vers les champs.
- [ ] Envoi valide : état occupé, second clic sans nouvelle soumission.
- [ ] Retour navigateur : boutons réactivés ; aucune nouvelle opération déclenchée seule.
- [ ] Confirmation sensible : Revenir/Échap annulent ; Confirmer soumet une seule fois.
- [ ] Sans JS : formulaires POST, CSRF, confirmations HTML existantes et navigation fonctionnent.

### Réseau et listes

- [ ] Aucun appel à un CDN, une police ou une bibliothèque distante.
- [ ] Ressources déjà chargées utilisables avec le réseau coupé ; les opérations métier exigent toujours le serveur.
- [ ] Recherche : la saisie déclenche un GET après temporisation, sans soumission POST.
- [ ] Résultats de l’ensemble du catalogue, pagination préservée, état de chargement annoncé.
- [ ] Une ancienne réponse lente ne remplace pas une réponse plus récente.
- [ ] Si fetch échoue : message explicite et bouton Rechercher toujours utilisable.
- [ ] Retrait d’une chip : les autres filtres restent appliqués ; « Tout effacer » réinitialise.
- [ ] Actualisation et pagination conservent les paramètres GET ; aucune promesse de persistance hors URL.

## Parcours par rôle

| Rôle | Parcours à vérifier | Actions qui ne doivent pas apparaître |
|---|---|---|
| Caissier | Ouvrir vente comptoir, rechercher/scanner, quantité, FEFO, espèces, monnaie, reçu, vente suivante | Vérifier un paiement électronique, retour, inventaire, gestion des comptes |
| Gestionnaire de stock | Fournisseur, commande, ajout/retrait en brouillon, validation, réceptions partielles, inventaire et blocage | Encaissement et retours sans rôle supplémentaire |
| Pharmacien responsable | Contrôle des médicaments/lots, ordonnance, vérification d’un paiement électronique, retour avec/sans remise en stock | Gestion des comptes sans rôle supplémentaire |
| Responsable de gestion | Dashboard, périodes, ventes, achats, lots, rapports et audit | Création/modification métier, encaissement, réception, inventaire, retour |
| Administrateur | Gestion des comptes et rôles, activation, tous les parcours métier | Modification d’un superadministrateur si le compte n’est pas lui-même superadministrateur |
| Rôles cumulés | Navigation et actions correspondant à l’union des permissions | Toute action non accordée par les rôles cumulés |

### Caisse : test détaillé

- [ ] Ouvrir une vente anonyme puis une vente avec client.
- [ ] F2 place le focus dans la recherche ; scanner un code-barres exact et presser Entrée.
- [ ] Le produit est présélectionné ; la quantité reçoit le focus ; Entrée ajoute uniquement au panier.
- [ ] Recherche nominale avec plusieurs résultats : choisir le produit sans déclencher d’encaissement.
- [ ] Quantité répartie sur deux lots : lignes et total corrects, suggestion FEFO cohérente avec les quantités déjà au panier.
- [ ] Lot sous 90 jours : avertissement lisible avec texte et icône ; choix spécifique toujours possible.
- [ ] Lot bloqué/périmé ou stock modifié avant encaissement : le serveur refuse la vente avec un message visible.
- [ ] F4 rejoint le paiement sans valider ; les espèces sont proposées par défaut.
- [ ] Total 15 000,00 Ar, montant reçu 20 000,00 : monnaie 5 000,00 Ar.
- [ ] Tester `20000`, `20 000,00`, `20000.00`, montant insuffisant, vide et texte invalide.
- [ ] Le calcul de monnaie ne modifie pas les montants comptables et n’affirme pas qu’un paiement est réalisé.
- [ ] Contrôler l’ordonnance si requise ; confirmation explicite ; double clic sans double sortie de stock.
- [ ] Après succès : référence, montant, reçu PDF, impression HTML et nouvelle vente disponibles selon droits.
- [ ] Chronométrer cinq ventes simples d’un article depuis une caisse ouverte : noter médiane, latence et conditions. Cible indicative : moins de 30 secondes, résultat à mesurer.

### Réception

- [ ] Commande sans effet sur stock ; récapitulatif commandé/reçu/restant cohérent.
- [ ] Réception de 8 sur 20 : stock +8, reliquat 12 ; enregistrer ensuite le reliquat.
- [ ] Numéro de lot et date obligatoires, erreurs compréhensibles.
- [ ] Double clic sans réception doublée ; bons PDF disponibles.

### Inventaire et retour

- [ ] Stock avant comptage affiché ; comptage et motif obligatoires ; différence visible dans les mouvements.
- [ ] Blocage expliqué et effectif pour la caisse.
- [ ] Retour : vente/lot d’origine, vendu/déjà retourné/encore retournable et prix visibles.
- [ ] Quantité excessive refusée ; référence du remboursement déjà effectué obligatoire.
- [ ] Retour sans remise en stock : aucun ajout ; retour éligible : ajout exact.
- [ ] Lot périmé ou bloqué : remise en stock refusée.

### Connexion, documents et impression

- [ ] Afficher/masquer le mot de passe préserve la valeur et annonce l’état du bouton.
- [ ] Erreur de connexion claire, mot de passe non réaffiché après échec.
- [ ] Impression HTML : pas de menus, champs de paiement ou boutons ; lignes non coupées et en-têtes de tableau répétés.
- [ ] Reçu/facture/rapports PDF téléchargés, lisibles dans le lecteur PDF.
- [ ] Contrôler les captures et l’aperçu d’impression avant la démonstration.

## Script de contrôle navigateur facultatif

`tools/ux_browser_check.cjs` ne valide aucune vente et ne modifie aucun stock. Il se connecte avec un compte de test, vérifie les pages accessibles à ce rôle, les quatre largeurs, les débordements, les dimensions des cibles, le tiroir, la monnaie indicative si une vente en brouillon est fournie, l’absence d’erreurs JS et de ressources distantes. Il prend des captures et vérifie les pages sans JS. Les mesures automatiques ne remplacent pas l’examen visuel ni un lecteur d’écran.

Il nécessite une installation de **Playwright** avec navigateur, indépendante de l’application. Exemple dans un terminal disposant de cette dépendance :

```bash
export PHARMAGEST_USERNAME=compte_fictif
read -rs -p 'Mot de passe : ' PHARMAGEST_PASSWORD
export PHARMAGEST_PASSWORD
node tools/ux_browser_check.cjs
unset PHARMAGEST_PASSWORD
```

Variables optionnelles :

| Variable | Usage |
|---|---|
| `PHARMAGEST_URL` | Serveur local, par défaut `http://127.0.0.1:8000` |
| `PHARMAGEST_SALE_ID` | Identifiant d’une vente pour inclure la caisse |
| `UX_ROUTES` | Chemins séparés par virgules, à adapter au rôle ; par défaut dashboard/catalogue/stocks/achats/ventes/rapports |
| `UX_OUTPUT_DIR` | Dossier des captures et résultats ; par défaut `/tmp/pharmagest-ux` |
| `PLAYWRIGHT_MODULE_PATH` | Chemin d’un package Playwright déjà installé si non résolu par Node |
| `CHROME_PATH` | Chemin du binaire Chrome si nécessaire |

Pour un caissier, retirer `/achats/` de `UX_ROUTES`. Pour un gestionnaire de stock, retirer `/ventes/` et ne pas fournir de vente. Un refus 403 est attendu sur les routes interdites ; le script de rendu les traite comme une erreur de configuration de son périmètre, et les tests Django couvrent séparément leur protection.

## Évolutions différées

Tendances KPI et séries temporelles réellement calculées côté serveur ; tri serveur global supplémentaire ; actions en masse avec prévisualisation et droits adaptés ; thème sombre complet ; lecteur de code-barres caméra ; raccourcis personnalisables ; mode hors ligne avec stratégie de synchronisation des stocks et paiements.

## Non-régression lors de la préparation du lanceur

Le 30 octobre 2026 : 85 tests Django réussis (158,444 s), 21 tests JS réussis, check Django sans anomalie, compilation du lanceur Python et syntaxe du script Node valides. Aucun changement de code métier ou de template applicatif dans cette étape. Ces résultats ne remplacent pas les cases de recette navigateur laissées à vérifier ci-dessus.

## Premier passage navigateur sur l'hôte — 30 octobre 2026

Rapport fourni : `/tmp/pharmagest-ux-report-sn78_rcg`. Pour l'administrateur, les 11 pages prévues à 360 px et le dashboard à 768 px passent les assertions avec JS ; arrêt au catalogue à 768 px. Les autres largeurs, rôles et le repli sans JS ne sont pas validés par ce passage.

La capture `administrateur/echec.png` montre des colonnes comprimées (noms, badges et actions coupés lettre par lettre). Le contrôle signalait également des liens Modifier/Archiver appartenant à des menus fermés : leurs rectangles ne prouvaient pas leur visibilité.

Corrections : largeur minimale du catalogue au-dessus de 600 px avec défilement dans le conteneur, noms de produit lisibles, mots des badges et menus préservés ; actions sur une colonne en cartes mobiles. Le contrôle ignore désormais les descendants masqués des details fermés et vérifie séparément le premier menu ouvert au clavier, les dimensions de ses liens et l'absence de débordement de page. Aucun seuil tactile abaissé. Nouvelle exécution navigateur nécessaire après ces corrections. Le 404 favicon n'est pas l'assertion qui a interrompu ce passage.

### Retour hôte z_0k5lok — 30 octobre 2026

Le catalogue à 768 px passe après correction ; 20 parcours de page avec JS sont enregistrés comme réussis pour l'administrateur (11 à 360 px, neuf à 768 px). Arrêt sur la création de médicament : le scénario attend le champ prix alors que la capture montre toujours Identification. Cause exacte du non-avancement non démontrée. Le scénario active maintenant Continuer au clavier et vérifie l'étape atteinte, avec restitution des messages inline si elle reste bloquée. Aucun changement de validation applicative. Syntaxe Node et diff vérifiés ; nouvelle exécution hôte requise, les autres rôles et le sans-JS restent non validés.

## Lot 1 — diagnostic avant correctif (reprise à 27ed6f6)

**Aucune cause racine démontrée à ce stade.** Les changements précédents du scénario (activation de Continuer au clavier) ne constituent pas une résolution attestée de l'assistant. Le rapport z_0k5lok prouve un champ prix masqué ; le rapport 6zmmb904 prouve une attente de stabilité du bouton de période. Ils ne prouvent pas leur cause.

La lecture de `forms.js` montre que seuls les `form[method="post"]` sont traités. Le GET du dashboard n'est donc pas mis en `noValidate` par ce script. L'assistant, lui, valide uniquement l'étape courante dans `forward()`, puis `show()` masque les autres étapes. Cela ne remplace pas une reproduction navigateur.

### Exécution hôte requise

```bash
.venv/bin/python tools/run_ux_review.py --diagnose-lot1
```

Aucun nouveau paquet requis : réutilisation du Playwright et du navigateur déjà utilisés sur le poste. Base et médias temporaires, administrateur fictif, aucune soumission finale de médicament, aucune vente. Le script ne force pas les clics, n'ajoute pas de sleep et ne change pas les validateurs. Les clics du dashboard restent associés à `waitForURL` dans `Promise.all` ; Entrée depuis la date de fin est aussi testée.

Le dossier annoncé contient `administrateur/lot1.json`, douze captures et `administrateur.log`. Pour chaque cas : état des contrôles (required/disabled/willValidate/valid/visible), noValidate réel, focus, messages inline et erreurs JS. Avec JS : séquence pointer/focus/click/submit et échantillons de géométrie/couverture du bouton. Les cookies d'authentification ne sont pas écrits dans le rapport. Les douze cas sont parcourus même si un cas est KO.

Après transmission du rapport, comparer événements et géométrie, conclure bug produit ou scénario erroné, puis créer le correctif minimal et le test qui échoue avant celui-ci. Le lot 1 reste **en cours** ; la matrice du lot 2 et les lots suivants attendent ce diagnostic, conformément à l'ordre demandé.

### Résultats réels de cette reprise

Chrome direct : **non exécuté après échec de lancement**, `setsockopt: Operation not permitted`. Le lanceur de diagnostic échoue avant Playwright : socket locale refusée (`Operation not permitted`), rapport `/tmp/pharmagest-ux-report-ghyjmdhn/summary.json`. Aucun cas du nouveau diagnostic n'a été exécuté dans un navigateur ici.

| Page / contrôle | Rôle | Largeur | JS | Thème | Résultat réel | Preuve |
|---|---|---:|---|---|---|---|
| Médicament — étape 1, souris | Administrateur | 360 | Avec | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Médicament — étape 1, clavier | Administrateur | 360 | Avec | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Dashboard — période, souris | Administrateur | 360 | Avec | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Dashboard — période, Entrée | Administrateur | 360 | Avec | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Dashboard — période, souris | Administrateur | 360 | Sans | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Dashboard — période, Entrée | Administrateur | 360 | Sans | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Médicament — étape 1, souris | Administrateur | 768 | Avec | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Médicament — étape 1, clavier | Administrateur | 768 | Avec | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Dashboard — période, souris | Administrateur | 768 | Avec | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Dashboard — période, Entrée | Administrateur | 768 | Avec | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Dashboard — période, souris | Administrateur | 768 | Sans | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |
| Dashboard — période, Entrée | Administrateur | 768 | Sans | Clair | non exécuté — socket refusée | Rapport de lancement ci-dessus ; aucune capture |

### Bilan intermédiaire du lot 1

- Fichiers : `tools/ux_lot1_diagnose.cjs` (nouveau diagnostic), `tools/run_ux_review.py` (option dédiée), ce guide et mémoire de reprise. Avant : attente de champ ou de clic sans trace suffisante. Après : reproductions séparées et état du formulaire, événements et géométrie conservés pour chaque cas.
- Tests navigateur ajoutés mais **non exécutés** : quatre passages assistant et huit passages période. Aucun test de non-régression produit « échec avant / succès après » revendiqué, puisqu'aucun correctif produit n'est encore justifié.
- Vérifications réellement exécutées : **85 tests Django réussis en 158,053 s**, check Django, absence de différence de migration, **12 + 9 tests JS réussis**, syntaxe Node et compilation Python. Préparation isolée : 45 rendus serveur.
- État des autres lots : lot 2 non commencé en attente du rapport ; lots 3 à 7 à suivre dans l'ordre ; lot 8 non autorisé et non commencé. Le bilan final et le plan des options seront produits après ces étapes, pas présentés comme achevés ici.

## Lot 1 — rapport hôte 426mt8qc, résultats observés

Douze cas exécutés sur le poste : **11 OK, 1 KO**. L'assistant avance à Prix dans les quatre essais, avec focus sur la légende et sans erreur JS. Les sept navigations de période réussies ont noValidate=false ; le cas KO aussi. Dans le KO, les dates sont valides et le focus reste sur la date de fin, sans changement d'URL. Cela ne prouve ni une superposition ni un défaut de validation. La cause du clic non reçu reste inconnue ; les échecs initiaux ne sont pas reproduits à l'identique.

| Page | Rôle | Largeur | JS | Thème | Activation | Résultat réel | Capture |
|---|---|---:|---|---|---|---|---|
| Médicament étape 1 | Administrateur | 360 | Avec | Clair | mouse | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/wizard-360-js-mouse.png` |
| Médicament étape 1 | Administrateur | 360 | Avec | Clair | keyboard | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/wizard-360-js-keyboard.png` |
| Dashboard période | Administrateur | 360 | Avec | Clair | mouse | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/dashboard-360-js-mouse.png` |
| Dashboard période | Administrateur | 360 | Avec | Clair | keyboard | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/dashboard-360-js-keyboard.png` |
| Dashboard période | Administrateur | 360 | Sans | Clair | mouse | KO | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/dashboard-360-sans-js-mouse.png` |
| Dashboard période | Administrateur | 360 | Sans | Clair | keyboard | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/dashboard-360-sans-js-keyboard.png` |
| Médicament étape 1 | Administrateur | 768 | Avec | Clair | mouse | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/wizard-768-js-mouse.png` |
| Médicament étape 1 | Administrateur | 768 | Avec | Clair | keyboard | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/wizard-768-js-keyboard.png` |
| Dashboard période | Administrateur | 768 | Avec | Clair | mouse | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/dashboard-768-js-mouse.png` |
| Dashboard période | Administrateur | 768 | Avec | Clair | keyboard | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/dashboard-768-js-keyboard.png` |
| Dashboard période | Administrateur | 768 | Sans | Clair | mouse | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/dashboard-768-sans-js-mouse.png` |
| Dashboard période | Administrateur | 768 | Sans | Clair | keyboard | OK | `/tmp/pharmagest-ux-report-426mt8qc/administrateur/dashboard-768-sans-js-keyboard.png` |

Le nouveau diagnostic ajoute uniquement des observations : demandes de navigation sans cookies, sonde d'événements injectée en lecture seule aussi dans le contexte sans scripts applicatifs, géométrie/couverture, capture du viewport avant activation et message KO détaillé dans le terminal. Les résultats précédents ne valident pas ces nouvelles observations. Aucun changement d'assistant, CSS, vue ou validation. Aucune cause hypothétique transformée en correctif.

Relancer seulement le cas intermittent, cinq fois :

```bash
.venv/bin/python tools/run_ux_review.py --diagnose-lot1 --lot1-case dashboard-360-sans-js-mouse --lot1-repeat 5
```

Le diagnostic reste sans sleep, clic forcé, deuxième clic automatique ou changement de focus destiné à contourner l'échec. Le mode complet reste disponible sans ces deux options. La recette globale et les lots suivants restent en attente de conclusion sur le lot 1.

## Lot 1 reporté, lot 2 autorisé — rapport 8d0__y96

À la demande de l'utilisateur, le défaut restant est reporté afin de poursuivre la matrice de présentation. **Il n'est pas résolu.** Sur cinq essais du clic de période à 360 px sans JS : un OK, quatre KO (trois attentes de navigation et une attente de stabilité du clic). Les dates sont valides. Les sondes d'événements/frames sont vides dans ce contexte sans JS ; aucune cause racine n'est donc déduite de ces tableaux vides. La position du bouton avant le clic peut être hors viewport ; cela ne démontre pas une couverture après le défilement automatique de Playwright.

| Page | Rôle | Largeur | JS | Thème | Essai | Résultat réel | Preuve |
|---|---|---:|---|---|---:|---|---|
| Dashboard période | Administrateur | 360 | Sans | Clair | 1 | KO | `/tmp/pharmagest-ux-report-8d0__y96/administrateur/dashboard-360-sans-js-mouse-essai-1.png` |
| Dashboard période | Administrateur | 360 | Sans | Clair | 2 | KO | `/tmp/pharmagest-ux-report-8d0__y96/administrateur/dashboard-360-sans-js-mouse-essai-2.png` |
| Dashboard période | Administrateur | 360 | Sans | Clair | 3 | KO | `/tmp/pharmagest-ux-report-8d0__y96/administrateur/dashboard-360-sans-js-mouse-essai-3.png` |
| Dashboard période | Administrateur | 360 | Sans | Clair | 4 | OK | `/tmp/pharmagest-ux-report-8d0__y96/administrateur/dashboard-360-sans-js-mouse-essai-4.png` |
| Dashboard période | Administrateur | 360 | Sans | Clair | 5 | KO | `/tmp/pharmagest-ux-report-8d0__y96/administrateur/dashboard-360-sans-js-mouse-essai-5.png` |

## Lot 2 — matrice indépendante des interactions reportées

```bash
.venv/bin/python tools/run_ux_review.py --matrix
```

Le mode `--matrix` conserve le lanceur isolé et utilise `tools/ux_matrix_check.cjs`, sans nouvelle dépendance. Il couvre les cinq rôles, 360/768/1280/1920 px, JS activé/désactivé, schéma système clair/sombre. Les 45 routes représentatives produisent **720 cas prévus**, pas 720 réussites. Le lot ne crée pas d'opération métier ; il se connecte uniquement aux comptes fictifs.

Chaque rôle reçoit un `matrix.json` : page, rôle, largeur, JS, thème, résultat réel OK/KO/non exécuté, liste des assertions passées, défauts mesurés et nom de capture. Les cas sont initialisés « non exécuté » ; les échecs par page sont conservés et n'empêchent pas de parcourir les autres pages, thèmes et rôles. En cas d'interruption, les résultats partiels restent lisibles.

Contrôles automatisés : réponse HTTP, langue/titre unique, schéma de couleur calculé, débordement global, dimensions des cibles visibles, navigation active, lien d'évitement et focus, tiroir (inertie, boucle clavier, Échap et restitution du focus), navigation sans JS, erreurs JS et ressources distantes. Les six premières étapes de tabulation sont consignées. Les textes potentiellement débordants sont signalés pour inspection, sans être arbitrairement qualifiés de défauts.

**Contrôles différés déclarés dans chaque rapport :** activation du filtre de période (défaut connu), examen visuel et texte tronqué, ordre complet du clavier/lecteur d'écran, erreurs après saisie et soumission métier, zoom et impression. La matrice ne remplace donc pas les parcours détaillés. Si toutes ses assertions passent, le résumé reste `incomplete_known_defects` tant que ces vérifications et le défaut connu sont ouverts ; aucun succès global n'est annoncé.

### Exécution depuis l'environnement de l'agent

Tentative `--matrix` : **non exécuté dans un navigateur**, ouverture du socket local refusée, rapport `/tmp/pharmagest-ux-report-kfbqsr68/summary.json`. Aucune capture de matrice produite ici.

| Pages prévues | Rôles | Largeurs | JS | Thèmes | Résultat réel | Preuve |
|---|---|---|---|---|---|---|
| 45 routes représentatives selon droits | 5 | 360/768/1280/1920 | Avec et sans | Clair et sombre | non exécuté — socket refusé | `/tmp/pharmagest-ux-report-kfbqsr68/summary.json` ; aucune capture |

Après exécution sur le poste, les lignes des fichiers `matrix.json` seront reportées dans ce document avec les captures existantes. Les contrôles non exécutés ne seront pas transformés en OK.

## Comparatif mono-thread / multi-thread — 30 octobre 2026

Hypothèse utilisateur : `wsgiref` mono-thread attend une requête sur une connexion de préchauffage, retardant les suivantes. Le code antérieur utilise bien WSGIServer mono-thread. **Cela ne démontre pas la cause des clics échoués.**

Le lanceur expose `--server single|threaded`, avec ThreadedWSGIServer de Django par défaut. Les deux modes emploient le même handler HTTP/1.0, la même file d'attente et la même application ; aucun timeout de lecture n'est introduit pour contourner l'hypothèse. Les clients sont fermés seulement au nettoyage, après la fin de Chrome.

`requests.jsonl` journalise en UTC milliseconde les connexions acceptées, démarrages de handler, en-têtes reçus, entrée WSGI, début/fin de réponse et fermeture. Aucune valeur de cookie, en-tête ou corps n'est persistée ; seuls le chemin et les dates start/end sont conservés. `summary.json` contient les compteurs et la chronologie des requêtes HTTP, ainsi que les passages réellement exécutés. Une connexion sans en-têtes peut être un préchauffage normal : elle ne prouve un blocage que si les traces montrent qu'elle retarde les requêtes suivantes en mono-thread.

### Tentatives réellement exécutées ici

| Mode | Horodatage de la demande de lancement UTC | Passages demandés | Passages navigateur exécutés | Requêtes HTTP reçues | Résultat | Rapport |
|---|---|---:|---:|---:|---|---|
| single | 2026-10-30 08:17:48.100 | 10 | 0 | 0 | non exécuté — socket refusé avant écoute | `/tmp/pharmagest-ux-report-n01o0e0c/summary.json` |
| threaded | 2026-10-30 08:17:57.602 | 20 | 0 | 0 | non exécuté — socket refusé avant écoute | `/tmp/pharmagest-ux-report-01vc845r/summary.json` |

Il n'existe donc aucun horaire d'arrivée HTTP pour ces tentatives. Les zéros ne sont ni dix/vingt succès ni dix/vingt échecs de l'interface. Premières tentatives également bloquées : zk3xhjg_ et 0u5jb751. Aucun avant/après navigateur ne permet de conclure ici.

### Commandes sur le poste, sur la même version des fichiers

```bash
.venv/bin/python tools/run_ux_review.py --server single --diagnose-lot1 --lot1-case dashboard-360-sans-js-mouse --lot1-repeat 10
.venv/bin/python tools/run_ux_review.py --server threaded --diagnose-lot1 --lot1-case dashboard-360-sans-js-mouse --lot1-repeat 20
```

Exécuter la seconde commande même si la première finit en KO. Transmettre les deux dossiers annoncés, notamment `summary.json`, `requests.jsonl` et `administrateur/lot1.json`. Le diagnostic inclut désormais checkValidity du GET, elementFromPoint, les résultats séparés du clic et de l'attente de navigation, et une trace JSON horodatée côté Playwright. Ces traces excluent les cookies et mots de passe ; aucune archive Playwright brute contenant des en-têtes d'authentification n'est créée.

Comparer d'abord les passages réellement exécutés, OK/KO et les GET portant les dates. Relier leurs heures aux connexions sans en-têtes et au début/à la fin des réponses. Une différence de taux seule n'établit pas le préchauffage comme cause. Si le comparatif n'établit pas la cause, conserver le défaut ouvert et examiner les traces de cible, validité et navigation.

### Favicon et couleur de navigateur

SVG local `static/icons/favicon.svg` déclaré dans base.html. Deux meta theme-color, avec media clair/sombre, fonctionnent sans JS ; theme.js synchronise leur contenu avec le choix manuel, le changement du système et les autres onglets. Aucune route, vue, permission ou modèle modifié. Le handler statique sert le SVG en 200 ; l'absence de requête automatique `/favicon.ico` reste à confirmer dans un navigateur réel.

Vérifications exécutées : trois tests Python de journalisation/comparabilité sans socket ; cinq tests Node de thème, puis les douze tests JS caisse et neuf opérations ; check Django sans anomalie ; douze tests Django de présentation/métadonnées, puis deux tests de métadonnées après ajout du contrôle HTTP statique. Suite Django complète non réexécutée pour cette étape. Ces contrôles ne constituent pas un comparatif réseau.

## Comparatif exécuté sur le poste — 2 novembre 2026

Rapports `_0hmnjzp` et `e8jza826` inspectés :

| Mode | Passages | OK | KO | HTTP reçus / terminés | Connexions acceptées sans en-têtes | GET de période |
|---|---:|---:|---:|---:|---:|---:|
| single | 10 | 1 | 9 | 85 / 85 | 0 | 1 |
| threaded | 20 | 0 | 20 | 154 / 154 | 0 | 0 |

Périodes UTC : single 05:27:09.623–05:28:42.082 ; threaded 05:28:55.803–05:32:00.617. Le seul GET de période est reçu à 05:27:25.513 UTC. Durées WSGI médianes/maximales : single 2,01/1661,73 ms ; threaded 4,92/1695,02 ms (toutes routes, authentification incluse). Les 29 échecs portent sur l'activation Playwright (`element is not stable`) avant un GET de période. checkValidity du formulaire reste vrai. Les sondes de frames et d'événements sont vides sans JS.

**Conclusion limitée :** aucune amélioration multi-thread et aucune connexion sans en-têtes dans ces traces. Le comparatif ne soutient pas l'hypothèse du préchauffage comme cause des échecs observés. Il ne démontre pas encore une cause alternative. Aucune modification du dashboard n'en découle.

### Témoin navigateur indépendant

```bash
.venv/bin/python tools/run_ux_review.py --probe-browser
```

Ce mode ne prépare pas Django, n'ouvre pas de serveur et ne lit pas la base. Il affiche seulement un bouton synthétique statique et compare JS activé/désactivé : clic normal par locator, compteur requestAnimationFrame, géométrie avant/après, visibilité du document et focus. Un clic physique aux coordonnées sert de contrôle sur cette page synthétique seulement ; il ne remplace aucun clic dans la recette produit et ne compte pas comme résolution du défaut.

Le rapport `browser-probe.json` indique les versions réellement utilisées et si un Chromium embarqué déjà présent peut servir de second témoin. Aucune installation ou mise à jour automatique. Traces Playwright ZIP et captures limitées au bouton synthétique sans authentification : aucun cookie de session PharmaGest ni mot de passe dans ces archives.

Versions observées localement : package Playwright du cache Go 1.50.1, binaire google-chrome 145.0.7632.109 ; browsers.json du package annonce Chromium 133.0.6943.16. Les anciens rapports ne consignaient pas leurs versions, donc cet écart est une piste et non une cause établie. Si le clic échoue aussi sur le témoin sans serveur, chercher d'abord du côté navigateur/automatisation ; s'il passe, poursuivre l'analyse des géométries de la vraie page.

Tentative du témoin ici : lancement Chrome bloqué avant les cas, rapport `/tmp/pharmagest-ux-report-wjqmsqcq/browser-probe.json`. Aucun résultat de clic du témoin exécuté ici. Vérifications actuelles : syntaxe Node, compilation Python, trois tests de journalisation sans socket réussis (0,125 s), diff sans erreur. Aucun changement applicatif dans cette analyse.

## Témoin m7tpz2it — 2 novembre 2026

Rapport du poste lu : Playwright 1.50.1 / Chrome 145.0.7632.109, aucun Chromium embarqué installé. **Le clic locator réussit avec ET sans JS** sur le bouton dans le viewport. Géométrie document stable, focus reçu par le bouton. Le compteur rAF de page vaut 0 sans JS alors que le clic réussit : cette absence de callback main-world ne prouve donc pas une panne du contrôle Playwright.

| Scénario | JS | Résultat réel | Preuve |
|---|---|---|---|
| Bouton synthétique dans le viewport | Avec | OK | `/tmp/pharmagest-ux-report-m7tpz2it/configured-js.png` et `browser-probe.json` |
| Bouton synthétique dans le viewport | Sans | OK | `/tmp/pharmagest-ux-report-m7tpz2it/configured-sans-js.png` et `browser-probe.json` |

L'écart de versions ne démontre pas à lui seul la cause du défaut. Une différence concrète à isoler est le défilement : Bootstrap local contient `@media (prefers-reduced-motion:no-preference){:root{scroll-behavior:smooth}}`, et le bouton réel est hors écran avant plusieurs clics échoués.

Le témoin est étendu à trois configurations avec/sans JS : bouton dans le viewport, bouton hors écran avec défilement auto, même bouton hors écran avec défilement smooth. Les deux cas hors écran remplissent une date placée avant le bouton pour reproduire le focus préalable. Coordonnées dans le document et dans le viewport sont séparées pour distinguer défilement normal et déplacement de layout. Aucune règle CSS applicative modifiée tant que le comparatif ne démontre pas la cause.

```bash
.venv/bin/python tools/run_ux_review.py --probe-browser
```

Ces six cas étendus restent à exécuter sur le poste. Un échec locator donne désormais aussi un code de sortie non nul et une ligne explicite dans le terminal ; les contrôles physiques sur le témoin ne sont jamais comptés comme une réussite de la recette applicative.

## Défilement animé isolé — témoin olrbhn5i, 2 novembre 2026

Les six conditions du témoin ont été exécutées sur le poste. Même bouton et même date dans les deux cas hors écran, seul le mode de défilement change. Le clic échoue uniquement pour hors écran + smooth + JS désactivé ; la géométrie dans le document reste fixe dans les six cas.

| Scénario | JS | Défilement calculé | Clic locator réel | Géométrie document fixe | Capture |
|---|---|---|---|---|---|
| viewport | Avec | auto | OK | True | `/tmp/pharmagest-ux-report-olrbhn5i/configured-js-viewport.png` |
| offscreen-auto | Avec | auto | OK | True | `/tmp/pharmagest-ux-report-olrbhn5i/configured-js-offscreen-auto.png` |
| offscreen-smooth | Avec | smooth | OK | True | `/tmp/pharmagest-ux-report-olrbhn5i/configured-js-offscreen-smooth.png` |
| viewport | Sans | auto | OK | True | `/tmp/pharmagest-ux-report-olrbhn5i/configured-sans-js-viewport.png` |
| offscreen-auto | Sans | auto | OK | True | `/tmp/pharmagest-ux-report-olrbhn5i/configured-sans-js-offscreen-auto.png` |
| offscreen-smooth | Sans | smooth | KO | True | `/tmp/pharmagest-ux-report-olrbhn5i/configured-sans-js-offscreen-smooth.png` |

### Correctif minimal et validation restante

Dans `static/css/app.css`, `:root { scroll-behavior: auto; }` surcharge la règle smooth globale de Bootstrap. Avant : animation de défilement héritée, cas réel sans JS 29 KO/30 lors du comparatif réseau. Après : défilement immédiat, sans changement de clic, validation, formulaire ou vue. Le diagnostic enregistre désormais la valeur calculée de scrollBehavior.

La condition d'échec est isolée sur le témoin ; le mécanisme interne exact de Chrome/Playwright n'est pas affirmé. Le succès du correctif sur la vraie page reste **non exécuté ici**, le navigateur étant bloqué dans cet environnement. Le test de non-régression est le même scénario réel déjà en échec avant correctif, sans sleep, clic forcé, répétition corrective ou changement de serveur destiné à le masquer :

```bash
.venv/bin/python tools/run_ux_review.py --server threaded --diagnose-lot1 --lot1-case dashboard-360-sans-js-mouse --lot1-repeat 20
```

Attendu à vérifier : scrollBehavior=auto, vingt GET de période et vingt passages OK. Ces valeurs sont des critères, pas des résultats acquis. Si ce contrôle passe, relancer le diagnostic complet du lot 1 et la matrice. Le témoin --probe-browser impose encore volontairement smooth dans son cas négatif : son KO synthétique ne constitue pas une mesure de l'application corrigée.

## Correction validée sur la page réelle — dbxll7ue, 2 novembre 2026

Rapport utilisateur inspecté : **20 passages demandés, 20 exécutés, 20 OK, 0 KO**, serveur threaded. Les vingt snapshots après navigation indiquent scrollBehavior=auto. Journal : 174 requêtes HTTP reçues dont vingt GET de période, dates start=2000-01-01 et end=2000-01-31.

| Page | Rôle | Largeur | JS | Thème | Résultat réel | Preuve |
|---|---|---:|---|---|---|---|
| Dashboard, clic sur période | Administrateur | 360 | Sans | Clair | OK — 20/20 | `/tmp/pharmagest-ux-report-dbxll7ue/administrateur/lot1.json` et captures associées ; `requests.jsonl` |

Avant correction dans le même mode : 0/20 dans e8jza826 ; après surcharge scroll-behavior:auto : 20/20 dans dbxll7ue. Le témoin à six variantes avait isolé la combinaison offscreen/smooth/sans JS. Le défaut précis de clic est donc validé après correction dans ce périmètre. Cela ne valide pas toute l'accessibilité ni les autres combinaisons de la matrice.

La matrice ne déclare plus ce défaut ouvert. Si ses assertions passent, son statut devient `automated_checks_ok_manual_review_pending` : examen visuel, texte, ordre complet du clavier et parcours métier restent à vérifier. Les mentions de défaut ouvert et d'anciens statuts dans les sections précédentes sont historiques.

### Lot 2 — nouvelle tentative locale

Commande --matrix tentée : socket refusé avant navigateur, rapport `/tmp/pharmagest-ux-report-wvpnl77f/summary.json`, zéro requête reçue et aucun cas navigateur exécuté. Commande à lancer sur le poste :

```bash
.venv/bin/python tools/run_ux_review.py --matrix
```

Cinq rôles × quatre largeurs × deux modes JS × deux thèmes, 720 pages prévues sur le jeu actuel. La suite collecte les KO et continue ; un dossier matrix.json par rôle conserve les preuves. Aucun résultat de cette nouvelle matrice n'est encore déclaré réussi.

## Matrice reçue uwt80wl_ — 2 novembre 2026

Rapports des cinq rôles inspectés : **720 assertions de page OK, zéro KO, zéro non exécuté**, 1534 HTTP reçus. Les 720 captures annoncées existent ; aucun débordement global, cible trop petite ou clipping signalé par les assertions. Toutes les seize combinaisons largeur/JS/thème contiennent 45 pages. Le statut reste `automated_checks_ok_manual_review_pending`.

Le champ revision désigne le commit de base 5db7d4a ; l'exécution porte sur les fichiers modifiés du répertoire de travail, pas uniquement sur le contenu de ce commit. Ce rapport précède la dernière retouche de largeur du tableau de stocks décrite ci-dessous.

| Rôle | Pages automatiques OK | KO |
|---|---:|---:|
| administrateur | 176 | 0 |
| caissier | 96 | 0 |
| gestion | 128 | 0 |
| pharmacien | 176 | 0 |
| stock | 144 | 0 |

### Inspection visuelle échantillonnée et retouche

Trois captures examinées : stocks sombre/sans JS/768, création médicament clair/JS/1280, dashboard sombre/JS/1920. L'examen n'est pas exhaustif. Le tableau des stocks à 768 px morcelle les noms et numéros de lots : **défaut visuel**, bien que les assertions géométriques passent. Cause visible : compression des colonnes avec retour anywhere, sans largeur minimale comme celle du catalogue.

Retouche minimale : classe stock-table sur le tableau, réutilisation de la largeur minimale 900 px au-dessus de 600 px, minimum de colonne médicament/lot ; défilement interne conservé. Les cartes mobiles restent inchangées. Nouvelle capture après retouche à vérifier avant de considérer ce défaut clos :

```bash
.venv/bin/python tools/run_ux_review.py --matrix --role stock
```

Ce passage ciblé produit 144 cas automatisés, dont 16 captures de stocks ; examiner en priorité stocks à 768 px clair/sombre, avec/sans JS. La recette complète des 720 cas précédents n'est pas déclarée rejouée après cette retouche. Le rendu serveur des pages principales passe après retouche (un test, 2,044 s).

### Détail des résultats automatiques et preuves

Les tableaux suivants transcrivent les matrix.json réellement reçus, sans modifier leurs résultats. Un OK signifie les assertions communes listées dans le rapport, pas une validation exhaustive de l'expérience. Les chemins /tmp doivent être conservés hors Git si l'on souhaite garder les captures après nettoyage de la machine. Aucun fichier de rapport ou capture brute n'est ajouté à l'index.

<details>
<summary>administrateur — résultats détaillés</summary>

| Page | Rôle | Largeur | JS | Thème | Résultat automatique | Capture |
|---|---|---:|---|---|---|---|
| / | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_.png` |
| /catalogue/medicaments/ | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_stocks_.png` |
| /rapports/ | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_rapports_.png` |
| /achats/ | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_achats_.png` |
| /achats/2/ | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_achats_2_.png` |
| /ventes/ | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_ventes_.png` |
| /achats/2/reception/ | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-360-_ventes_5_.png` |
| / | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_.png` |
| /catalogue/medicaments/ | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_stocks_.png` |
| /rapports/ | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_rapports_.png` |
| /achats/ | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_achats_.png` |
| /achats/2/ | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_achats_2_.png` |
| /ventes/ | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_ventes_.png` |
| /achats/2/reception/ | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-768-_ventes_5_.png` |
| / | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_.png` |
| /catalogue/medicaments/ | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_stocks_.png` |
| /rapports/ | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_rapports_.png` |
| /achats/ | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_achats_.png` |
| /achats/2/ | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_achats_2_.png` |
| /ventes/ | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_ventes_.png` |
| /achats/2/reception/ | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1280-_ventes_5_.png` |
| / | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_.png` |
| /catalogue/medicaments/ | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_stocks_.png` |
| /rapports/ | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_rapports_.png` |
| /achats/ | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_achats_.png` |
| /achats/2/ | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_achats_2_.png` |
| /ventes/ | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_ventes_.png` |
| /achats/2/reception/ | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-js-1920-_ventes_5_.png` |
| / | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_.png` |
| /catalogue/medicaments/ | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_stocks_.png` |
| /rapports/ | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_rapports_.png` |
| /achats/ | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_achats_.png` |
| /achats/2/ | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_achats_2_.png` |
| /ventes/ | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_ventes_.png` |
| /achats/2/reception/ | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-360-_ventes_5_.png` |
| / | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_.png` |
| /catalogue/medicaments/ | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_stocks_.png` |
| /rapports/ | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_rapports_.png` |
| /achats/ | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_achats_.png` |
| /achats/2/ | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_achats_2_.png` |
| /ventes/ | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_ventes_.png` |
| /achats/2/reception/ | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-768-_ventes_5_.png` |
| / | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_.png` |
| /catalogue/medicaments/ | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_stocks_.png` |
| /rapports/ | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_rapports_.png` |
| /achats/ | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_achats_.png` |
| /achats/2/ | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_achats_2_.png` |
| /ventes/ | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_ventes_.png` |
| /achats/2/reception/ | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1280-_ventes_5_.png` |
| / | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_.png` |
| /catalogue/medicaments/ | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_stocks_.png` |
| /rapports/ | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_rapports_.png` |
| /achats/ | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_achats_.png` |
| /achats/2/ | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_achats_2_.png` |
| /ventes/ | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_ventes_.png` |
| /achats/2/reception/ | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/light-sans-js-1920-_ventes_5_.png` |
| / | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_.png` |
| /catalogue/medicaments/ | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_stocks_.png` |
| /rapports/ | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_rapports_.png` |
| /achats/ | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_achats_.png` |
| /achats/2/ | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_achats_2_.png` |
| /ventes/ | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_ventes_.png` |
| /achats/2/reception/ | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-360-_ventes_5_.png` |
| / | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_.png` |
| /catalogue/medicaments/ | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_stocks_.png` |
| /rapports/ | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_rapports_.png` |
| /achats/ | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_achats_.png` |
| /achats/2/ | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_achats_2_.png` |
| /ventes/ | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_ventes_.png` |
| /achats/2/reception/ | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-768-_ventes_5_.png` |
| / | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_.png` |
| /catalogue/medicaments/ | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_stocks_.png` |
| /rapports/ | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_rapports_.png` |
| /achats/ | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_achats_.png` |
| /achats/2/ | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_achats_2_.png` |
| /ventes/ | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_ventes_.png` |
| /achats/2/reception/ | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1280-_ventes_5_.png` |
| / | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_.png` |
| /catalogue/medicaments/ | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_stocks_.png` |
| /rapports/ | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_rapports_.png` |
| /achats/ | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_achats_.png` |
| /achats/2/ | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_achats_2_.png` |
| /ventes/ | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_ventes_.png` |
| /achats/2/reception/ | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-js-1920-_ventes_5_.png` |
| / | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_.png` |
| /catalogue/medicaments/ | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_stocks_.png` |
| /rapports/ | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_rapports_.png` |
| /achats/ | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_achats_.png` |
| /achats/2/ | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_achats_2_.png` |
| /ventes/ | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_ventes_.png` |
| /achats/2/reception/ | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-360-_ventes_5_.png` |
| / | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_.png` |
| /catalogue/medicaments/ | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_stocks_.png` |
| /rapports/ | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_rapports_.png` |
| /achats/ | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_achats_.png` |
| /achats/2/ | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_achats_2_.png` |
| /ventes/ | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_ventes_.png` |
| /achats/2/reception/ | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-768-_ventes_5_.png` |
| / | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_.png` |
| /catalogue/medicaments/ | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_stocks_.png` |
| /rapports/ | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_rapports_.png` |
| /achats/ | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_achats_.png` |
| /achats/2/ | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_achats_2_.png` |
| /ventes/ | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_ventes_.png` |
| /achats/2/reception/ | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1280-_ventes_5_.png` |
| / | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_.png` |
| /catalogue/medicaments/ | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_stocks_.png` |
| /rapports/ | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_rapports_.png` |
| /achats/ | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_achats_.png` |
| /achats/2/ | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_achats_2_.png` |
| /ventes/ | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_ventes_.png` |
| /achats/2/reception/ | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_catalogue_medicaments_ajouter_.png` |
| /ventes/5/ | administrateur | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/dark-sans-js-1920-_ventes_5_.png` |

</details>

<details>
<summary>caissier — résultats détaillés</summary>

| Page | Rôle | Largeur | JS | Thème | Résultat automatique | Capture |
|---|---|---:|---|---|---|---|
| / | caissier | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-360-_.png` |
| /catalogue/medicaments/ | caissier | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-360-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-360-_stocks_.png` |
| /rapports/ | caissier | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-360-_rapports_.png` |
| /ventes/ | caissier | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-360-_ventes_.png` |
| /ventes/7/ | caissier | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-360-_ventes_7_.png` |
| / | caissier | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-768-_.png` |
| /catalogue/medicaments/ | caissier | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-768-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-768-_stocks_.png` |
| /rapports/ | caissier | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-768-_rapports_.png` |
| /ventes/ | caissier | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-768-_ventes_.png` |
| /ventes/7/ | caissier | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-768-_ventes_7_.png` |
| / | caissier | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1280-_.png` |
| /catalogue/medicaments/ | caissier | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1280-_stocks_.png` |
| /rapports/ | caissier | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1280-_rapports_.png` |
| /ventes/ | caissier | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1280-_ventes_.png` |
| /ventes/7/ | caissier | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1280-_ventes_7_.png` |
| / | caissier | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1920-_.png` |
| /catalogue/medicaments/ | caissier | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1920-_stocks_.png` |
| /rapports/ | caissier | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1920-_rapports_.png` |
| /ventes/ | caissier | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1920-_ventes_.png` |
| /ventes/7/ | caissier | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-js-1920-_ventes_7_.png` |
| / | caissier | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-360-_.png` |
| /catalogue/medicaments/ | caissier | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-360-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-360-_stocks_.png` |
| /rapports/ | caissier | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-360-_rapports_.png` |
| /ventes/ | caissier | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-360-_ventes_.png` |
| /ventes/7/ | caissier | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-360-_ventes_7_.png` |
| / | caissier | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-768-_.png` |
| /catalogue/medicaments/ | caissier | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-768-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-768-_stocks_.png` |
| /rapports/ | caissier | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-768-_rapports_.png` |
| /ventes/ | caissier | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-768-_ventes_.png` |
| /ventes/7/ | caissier | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-768-_ventes_7_.png` |
| / | caissier | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1280-_.png` |
| /catalogue/medicaments/ | caissier | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1280-_stocks_.png` |
| /rapports/ | caissier | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1280-_rapports_.png` |
| /ventes/ | caissier | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1280-_ventes_.png` |
| /ventes/7/ | caissier | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1280-_ventes_7_.png` |
| / | caissier | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1920-_.png` |
| /catalogue/medicaments/ | caissier | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1920-_stocks_.png` |
| /rapports/ | caissier | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1920-_rapports_.png` |
| /ventes/ | caissier | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1920-_ventes_.png` |
| /ventes/7/ | caissier | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/light-sans-js-1920-_ventes_7_.png` |
| / | caissier | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-360-_.png` |
| /catalogue/medicaments/ | caissier | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-360-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-360-_stocks_.png` |
| /rapports/ | caissier | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-360-_rapports_.png` |
| /ventes/ | caissier | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-360-_ventes_.png` |
| /ventes/7/ | caissier | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-360-_ventes_7_.png` |
| / | caissier | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-768-_.png` |
| /catalogue/medicaments/ | caissier | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-768-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-768-_stocks_.png` |
| /rapports/ | caissier | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-768-_rapports_.png` |
| /ventes/ | caissier | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-768-_ventes_.png` |
| /ventes/7/ | caissier | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-768-_ventes_7_.png` |
| / | caissier | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1280-_.png` |
| /catalogue/medicaments/ | caissier | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1280-_stocks_.png` |
| /rapports/ | caissier | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1280-_rapports_.png` |
| /ventes/ | caissier | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1280-_ventes_.png` |
| /ventes/7/ | caissier | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1280-_ventes_7_.png` |
| / | caissier | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1920-_.png` |
| /catalogue/medicaments/ | caissier | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1920-_stocks_.png` |
| /rapports/ | caissier | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1920-_rapports_.png` |
| /ventes/ | caissier | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1920-_ventes_.png` |
| /ventes/7/ | caissier | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-js-1920-_ventes_7_.png` |
| / | caissier | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-360-_.png` |
| /catalogue/medicaments/ | caissier | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-360-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-360-_stocks_.png` |
| /rapports/ | caissier | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-360-_rapports_.png` |
| /ventes/ | caissier | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-360-_ventes_.png` |
| /ventes/7/ | caissier | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-360-_ventes_7_.png` |
| / | caissier | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-768-_.png` |
| /catalogue/medicaments/ | caissier | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-768-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-768-_stocks_.png` |
| /rapports/ | caissier | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-768-_rapports_.png` |
| /ventes/ | caissier | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-768-_ventes_.png` |
| /ventes/7/ | caissier | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-768-_ventes_7_.png` |
| / | caissier | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1280-_.png` |
| /catalogue/medicaments/ | caissier | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1280-_stocks_.png` |
| /rapports/ | caissier | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1280-_rapports_.png` |
| /ventes/ | caissier | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1280-_ventes_.png` |
| /ventes/7/ | caissier | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1280-_ventes_7_.png` |
| / | caissier | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1920-_.png` |
| /catalogue/medicaments/ | caissier | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | caissier | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1920-_stocks_.png` |
| /rapports/ | caissier | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1920-_rapports_.png` |
| /ventes/ | caissier | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1920-_ventes_.png` |
| /ventes/7/ | caissier | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/caissier/dark-sans-js-1920-_ventes_7_.png` |

</details>

<details>
<summary>gestion — résultats détaillés</summary>

| Page | Rôle | Largeur | JS | Thème | Résultat automatique | Capture |
|---|---|---:|---|---|---|---|
| / | gestion | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-360-_.png` |
| /catalogue/medicaments/ | gestion | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-360-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-360-_stocks_.png` |
| /rapports/ | gestion | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-360-_rapports_.png` |
| /achats/ | gestion | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-360-_achats_.png` |
| /achats/2/ | gestion | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-360-_achats_2_.png` |
| /ventes/ | gestion | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-360-_ventes_.png` |
| /ventes/8/ | gestion | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-360-_ventes_8_.png` |
| / | gestion | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-768-_.png` |
| /catalogue/medicaments/ | gestion | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-768-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-768-_stocks_.png` |
| /rapports/ | gestion | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-768-_rapports_.png` |
| /achats/ | gestion | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-768-_achats_.png` |
| /achats/2/ | gestion | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-768-_achats_2_.png` |
| /ventes/ | gestion | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-768-_ventes_.png` |
| /ventes/8/ | gestion | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-768-_ventes_8_.png` |
| / | gestion | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1280-_.png` |
| /catalogue/medicaments/ | gestion | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1280-_stocks_.png` |
| /rapports/ | gestion | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1280-_rapports_.png` |
| /achats/ | gestion | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1280-_achats_.png` |
| /achats/2/ | gestion | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1280-_achats_2_.png` |
| /ventes/ | gestion | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1280-_ventes_.png` |
| /ventes/8/ | gestion | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1280-_ventes_8_.png` |
| / | gestion | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1920-_.png` |
| /catalogue/medicaments/ | gestion | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1920-_stocks_.png` |
| /rapports/ | gestion | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1920-_rapports_.png` |
| /achats/ | gestion | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1920-_achats_.png` |
| /achats/2/ | gestion | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1920-_achats_2_.png` |
| /ventes/ | gestion | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1920-_ventes_.png` |
| /ventes/8/ | gestion | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-js-1920-_ventes_8_.png` |
| / | gestion | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-360-_.png` |
| /catalogue/medicaments/ | gestion | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-360-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-360-_stocks_.png` |
| /rapports/ | gestion | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-360-_rapports_.png` |
| /achats/ | gestion | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-360-_achats_.png` |
| /achats/2/ | gestion | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-360-_achats_2_.png` |
| /ventes/ | gestion | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-360-_ventes_.png` |
| /ventes/8/ | gestion | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-360-_ventes_8_.png` |
| / | gestion | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-768-_.png` |
| /catalogue/medicaments/ | gestion | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-768-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-768-_stocks_.png` |
| /rapports/ | gestion | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-768-_rapports_.png` |
| /achats/ | gestion | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-768-_achats_.png` |
| /achats/2/ | gestion | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-768-_achats_2_.png` |
| /ventes/ | gestion | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-768-_ventes_.png` |
| /ventes/8/ | gestion | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-768-_ventes_8_.png` |
| / | gestion | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1280-_.png` |
| /catalogue/medicaments/ | gestion | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1280-_stocks_.png` |
| /rapports/ | gestion | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1280-_rapports_.png` |
| /achats/ | gestion | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1280-_achats_.png` |
| /achats/2/ | gestion | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1280-_achats_2_.png` |
| /ventes/ | gestion | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1280-_ventes_.png` |
| /ventes/8/ | gestion | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1280-_ventes_8_.png` |
| / | gestion | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1920-_.png` |
| /catalogue/medicaments/ | gestion | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1920-_stocks_.png` |
| /rapports/ | gestion | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1920-_rapports_.png` |
| /achats/ | gestion | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1920-_achats_.png` |
| /achats/2/ | gestion | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1920-_achats_2_.png` |
| /ventes/ | gestion | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1920-_ventes_.png` |
| /ventes/8/ | gestion | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/light-sans-js-1920-_ventes_8_.png` |
| / | gestion | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-360-_.png` |
| /catalogue/medicaments/ | gestion | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-360-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-360-_stocks_.png` |
| /rapports/ | gestion | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-360-_rapports_.png` |
| /achats/ | gestion | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-360-_achats_.png` |
| /achats/2/ | gestion | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-360-_achats_2_.png` |
| /ventes/ | gestion | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-360-_ventes_.png` |
| /ventes/8/ | gestion | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-360-_ventes_8_.png` |
| / | gestion | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-768-_.png` |
| /catalogue/medicaments/ | gestion | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-768-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-768-_stocks_.png` |
| /rapports/ | gestion | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-768-_rapports_.png` |
| /achats/ | gestion | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-768-_achats_.png` |
| /achats/2/ | gestion | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-768-_achats_2_.png` |
| /ventes/ | gestion | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-768-_ventes_.png` |
| /ventes/8/ | gestion | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-768-_ventes_8_.png` |
| / | gestion | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1280-_.png` |
| /catalogue/medicaments/ | gestion | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1280-_stocks_.png` |
| /rapports/ | gestion | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1280-_rapports_.png` |
| /achats/ | gestion | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1280-_achats_.png` |
| /achats/2/ | gestion | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1280-_achats_2_.png` |
| /ventes/ | gestion | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1280-_ventes_.png` |
| /ventes/8/ | gestion | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1280-_ventes_8_.png` |
| / | gestion | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1920-_.png` |
| /catalogue/medicaments/ | gestion | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1920-_stocks_.png` |
| /rapports/ | gestion | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1920-_rapports_.png` |
| /achats/ | gestion | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1920-_achats_.png` |
| /achats/2/ | gestion | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1920-_achats_2_.png` |
| /ventes/ | gestion | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1920-_ventes_.png` |
| /ventes/8/ | gestion | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-js-1920-_ventes_8_.png` |
| / | gestion | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-360-_.png` |
| /catalogue/medicaments/ | gestion | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-360-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-360-_stocks_.png` |
| /rapports/ | gestion | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-360-_rapports_.png` |
| /achats/ | gestion | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-360-_achats_.png` |
| /achats/2/ | gestion | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-360-_achats_2_.png` |
| /ventes/ | gestion | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-360-_ventes_.png` |
| /ventes/8/ | gestion | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-360-_ventes_8_.png` |
| / | gestion | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-768-_.png` |
| /catalogue/medicaments/ | gestion | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-768-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-768-_stocks_.png` |
| /rapports/ | gestion | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-768-_rapports_.png` |
| /achats/ | gestion | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-768-_achats_.png` |
| /achats/2/ | gestion | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-768-_achats_2_.png` |
| /ventes/ | gestion | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-768-_ventes_.png` |
| /ventes/8/ | gestion | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-768-_ventes_8_.png` |
| / | gestion | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1280-_.png` |
| /catalogue/medicaments/ | gestion | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1280-_stocks_.png` |
| /rapports/ | gestion | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1280-_rapports_.png` |
| /achats/ | gestion | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1280-_achats_.png` |
| /achats/2/ | gestion | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1280-_achats_2_.png` |
| /ventes/ | gestion | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1280-_ventes_.png` |
| /ventes/8/ | gestion | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1280-_ventes_8_.png` |
| / | gestion | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1920-_.png` |
| /catalogue/medicaments/ | gestion | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | gestion | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1920-_stocks_.png` |
| /rapports/ | gestion | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1920-_rapports_.png` |
| /achats/ | gestion | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1920-_achats_.png` |
| /achats/2/ | gestion | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1920-_achats_2_.png` |
| /ventes/ | gestion | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1920-_ventes_.png` |
| /ventes/8/ | gestion | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/gestion/dark-sans-js-1920-_ventes_8_.png` |

</details>

<details>
<summary>pharmacien — résultats détaillés</summary>

| Page | Rôle | Largeur | JS | Thème | Résultat automatique | Capture |
|---|---|---:|---|---|---|---|
| / | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_.png` |
| /catalogue/medicaments/ | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_stocks_.png` |
| /rapports/ | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_rapports_.png` |
| /achats/ | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_achats_.png` |
| /achats/2/ | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_achats_2_.png` |
| /ventes/ | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-360-_ventes_6_.png` |
| / | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_.png` |
| /catalogue/medicaments/ | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_stocks_.png` |
| /rapports/ | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_rapports_.png` |
| /achats/ | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_achats_.png` |
| /achats/2/ | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_achats_2_.png` |
| /ventes/ | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-768-_ventes_6_.png` |
| / | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_.png` |
| /catalogue/medicaments/ | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_stocks_.png` |
| /rapports/ | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_rapports_.png` |
| /achats/ | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_achats_.png` |
| /achats/2/ | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_achats_2_.png` |
| /ventes/ | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1280-_ventes_6_.png` |
| / | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_.png` |
| /catalogue/medicaments/ | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_stocks_.png` |
| /rapports/ | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_rapports_.png` |
| /achats/ | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_achats_.png` |
| /achats/2/ | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_achats_2_.png` |
| /ventes/ | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-js-1920-_ventes_6_.png` |
| / | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_.png` |
| /catalogue/medicaments/ | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_stocks_.png` |
| /rapports/ | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_rapports_.png` |
| /achats/ | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_achats_.png` |
| /achats/2/ | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_achats_2_.png` |
| /ventes/ | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-360-_ventes_6_.png` |
| / | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_.png` |
| /catalogue/medicaments/ | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_stocks_.png` |
| /rapports/ | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_rapports_.png` |
| /achats/ | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_achats_.png` |
| /achats/2/ | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_achats_2_.png` |
| /ventes/ | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-768-_ventes_6_.png` |
| / | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_.png` |
| /catalogue/medicaments/ | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_stocks_.png` |
| /rapports/ | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_rapports_.png` |
| /achats/ | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_achats_.png` |
| /achats/2/ | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_achats_2_.png` |
| /ventes/ | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1280-_ventes_6_.png` |
| / | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_.png` |
| /catalogue/medicaments/ | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_stocks_.png` |
| /rapports/ | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_rapports_.png` |
| /achats/ | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_achats_.png` |
| /achats/2/ | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_achats_2_.png` |
| /ventes/ | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/light-sans-js-1920-_ventes_6_.png` |
| / | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_.png` |
| /catalogue/medicaments/ | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_stocks_.png` |
| /rapports/ | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_rapports_.png` |
| /achats/ | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_achats_.png` |
| /achats/2/ | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_achats_2_.png` |
| /ventes/ | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-360-_ventes_6_.png` |
| / | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_.png` |
| /catalogue/medicaments/ | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_stocks_.png` |
| /rapports/ | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_rapports_.png` |
| /achats/ | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_achats_.png` |
| /achats/2/ | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_achats_2_.png` |
| /ventes/ | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-768-_ventes_6_.png` |
| / | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_.png` |
| /catalogue/medicaments/ | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_stocks_.png` |
| /rapports/ | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_rapports_.png` |
| /achats/ | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_achats_.png` |
| /achats/2/ | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_achats_2_.png` |
| /ventes/ | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1280-_ventes_6_.png` |
| / | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_.png` |
| /catalogue/medicaments/ | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_stocks_.png` |
| /rapports/ | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_rapports_.png` |
| /achats/ | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_achats_.png` |
| /achats/2/ | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_achats_2_.png` |
| /ventes/ | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-js-1920-_ventes_6_.png` |
| / | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_.png` |
| /catalogue/medicaments/ | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_stocks_.png` |
| /rapports/ | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_rapports_.png` |
| /achats/ | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_achats_.png` |
| /achats/2/ | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_achats_2_.png` |
| /ventes/ | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-360-_ventes_6_.png` |
| / | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_.png` |
| /catalogue/medicaments/ | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_stocks_.png` |
| /rapports/ | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_rapports_.png` |
| /achats/ | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_achats_.png` |
| /achats/2/ | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_achats_2_.png` |
| /ventes/ | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-768-_ventes_6_.png` |
| / | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_.png` |
| /catalogue/medicaments/ | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_stocks_.png` |
| /rapports/ | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_rapports_.png` |
| /achats/ | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_achats_.png` |
| /achats/2/ | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_achats_2_.png` |
| /ventes/ | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1280-_ventes_6_.png` |
| / | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_.png` |
| /catalogue/medicaments/ | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_stocks_.png` |
| /rapports/ | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_rapports_.png` |
| /achats/ | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_achats_.png` |
| /achats/2/ | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_achats_2_.png` |
| /ventes/ | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_ventes_.png` |
| /achats/2/reception/ | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_catalogue_medicaments_ajouter_.png` |
| /ventes/6/ | pharmacien | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/dark-sans-js-1920-_ventes_6_.png` |

</details>

<details>
<summary>stock — résultats détaillés</summary>

| Page | Rôle | Largeur | JS | Thème | Résultat automatique | Capture |
|---|---|---:|---|---|---|---|
| / | stock | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-360-_.png` |
| /catalogue/medicaments/ | stock | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-360-_catalogue_medicaments_.png` |
| /stocks/ | stock | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-360-_stocks_.png` |
| /rapports/ | stock | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-360-_rapports_.png` |
| /achats/ | stock | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-360-_achats_.png` |
| /achats/2/ | stock | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-360-_achats_2_.png` |
| /achats/2/reception/ | stock | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 360 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-360-_catalogue_medicaments_ajouter_.png` |
| / | stock | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-768-_.png` |
| /catalogue/medicaments/ | stock | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-768-_catalogue_medicaments_.png` |
| /stocks/ | stock | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-768-_stocks_.png` |
| /rapports/ | stock | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-768-_rapports_.png` |
| /achats/ | stock | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-768-_achats_.png` |
| /achats/2/ | stock | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-768-_achats_2_.png` |
| /achats/2/reception/ | stock | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 768 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-768-_catalogue_medicaments_ajouter_.png` |
| / | stock | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1280-_.png` |
| /catalogue/medicaments/ | stock | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | stock | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1280-_stocks_.png` |
| /rapports/ | stock | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1280-_rapports_.png` |
| /achats/ | stock | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1280-_achats_.png` |
| /achats/2/ | stock | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1280-_achats_2_.png` |
| /achats/2/reception/ | stock | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 1280 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1280-_catalogue_medicaments_ajouter_.png` |
| / | stock | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1920-_.png` |
| /catalogue/medicaments/ | stock | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | stock | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1920-_stocks_.png` |
| /rapports/ | stock | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1920-_rapports_.png` |
| /achats/ | stock | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1920-_achats_.png` |
| /achats/2/ | stock | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1920-_achats_2_.png` |
| /achats/2/reception/ | stock | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 1920 | Avec | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-js-1920-_catalogue_medicaments_ajouter_.png` |
| / | stock | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-360-_.png` |
| /catalogue/medicaments/ | stock | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-360-_catalogue_medicaments_.png` |
| /stocks/ | stock | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-360-_stocks_.png` |
| /rapports/ | stock | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-360-_rapports_.png` |
| /achats/ | stock | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-360-_achats_.png` |
| /achats/2/ | stock | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-360-_achats_2_.png` |
| /achats/2/reception/ | stock | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 360 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-360-_catalogue_medicaments_ajouter_.png` |
| / | stock | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-768-_.png` |
| /catalogue/medicaments/ | stock | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-768-_catalogue_medicaments_.png` |
| /stocks/ | stock | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-768-_stocks_.png` |
| /rapports/ | stock | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-768-_rapports_.png` |
| /achats/ | stock | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-768-_achats_.png` |
| /achats/2/ | stock | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-768-_achats_2_.png` |
| /achats/2/reception/ | stock | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 768 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-768-_catalogue_medicaments_ajouter_.png` |
| / | stock | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1280-_.png` |
| /catalogue/medicaments/ | stock | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | stock | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1280-_stocks_.png` |
| /rapports/ | stock | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1280-_rapports_.png` |
| /achats/ | stock | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1280-_achats_.png` |
| /achats/2/ | stock | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1280-_achats_2_.png` |
| /achats/2/reception/ | stock | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 1280 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1280-_catalogue_medicaments_ajouter_.png` |
| / | stock | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1920-_.png` |
| /catalogue/medicaments/ | stock | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | stock | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1920-_stocks_.png` |
| /rapports/ | stock | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1920-_rapports_.png` |
| /achats/ | stock | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1920-_achats_.png` |
| /achats/2/ | stock | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1920-_achats_2_.png` |
| /achats/2/reception/ | stock | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 1920 | Sans | Clair | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/light-sans-js-1920-_catalogue_medicaments_ajouter_.png` |
| / | stock | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-360-_.png` |
| /catalogue/medicaments/ | stock | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-360-_catalogue_medicaments_.png` |
| /stocks/ | stock | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-360-_stocks_.png` |
| /rapports/ | stock | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-360-_rapports_.png` |
| /achats/ | stock | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-360-_achats_.png` |
| /achats/2/ | stock | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-360-_achats_2_.png` |
| /achats/2/reception/ | stock | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 360 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-360-_catalogue_medicaments_ajouter_.png` |
| / | stock | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-768-_.png` |
| /catalogue/medicaments/ | stock | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-768-_catalogue_medicaments_.png` |
| /stocks/ | stock | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-768-_stocks_.png` |
| /rapports/ | stock | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-768-_rapports_.png` |
| /achats/ | stock | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-768-_achats_.png` |
| /achats/2/ | stock | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-768-_achats_2_.png` |
| /achats/2/reception/ | stock | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 768 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-768-_catalogue_medicaments_ajouter_.png` |
| / | stock | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1280-_.png` |
| /catalogue/medicaments/ | stock | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | stock | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1280-_stocks_.png` |
| /rapports/ | stock | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1280-_rapports_.png` |
| /achats/ | stock | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1280-_achats_.png` |
| /achats/2/ | stock | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1280-_achats_2_.png` |
| /achats/2/reception/ | stock | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 1280 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1280-_catalogue_medicaments_ajouter_.png` |
| / | stock | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1920-_.png` |
| /catalogue/medicaments/ | stock | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | stock | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1920-_stocks_.png` |
| /rapports/ | stock | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1920-_rapports_.png` |
| /achats/ | stock | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1920-_achats_.png` |
| /achats/2/ | stock | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1920-_achats_2_.png` |
| /achats/2/reception/ | stock | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 1920 | Avec | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-js-1920-_catalogue_medicaments_ajouter_.png` |
| / | stock | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-360-_.png` |
| /catalogue/medicaments/ | stock | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-360-_catalogue_medicaments_.png` |
| /stocks/ | stock | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-360-_stocks_.png` |
| /rapports/ | stock | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-360-_rapports_.png` |
| /achats/ | stock | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-360-_achats_.png` |
| /achats/2/ | stock | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-360-_achats_2_.png` |
| /achats/2/reception/ | stock | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-360-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-360-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 360 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-360-_catalogue_medicaments_ajouter_.png` |
| / | stock | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-768-_.png` |
| /catalogue/medicaments/ | stock | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-768-_catalogue_medicaments_.png` |
| /stocks/ | stock | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-768-_stocks_.png` |
| /rapports/ | stock | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-768-_rapports_.png` |
| /achats/ | stock | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-768-_achats_.png` |
| /achats/2/ | stock | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-768-_achats_2_.png` |
| /achats/2/reception/ | stock | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-768-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-768-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 768 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-768-_catalogue_medicaments_ajouter_.png` |
| / | stock | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1280-_.png` |
| /catalogue/medicaments/ | stock | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1280-_catalogue_medicaments_.png` |
| /stocks/ | stock | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1280-_stocks_.png` |
| /rapports/ | stock | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1280-_rapports_.png` |
| /achats/ | stock | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1280-_achats_.png` |
| /achats/2/ | stock | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1280-_achats_2_.png` |
| /achats/2/reception/ | stock | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1280-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1280-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 1280 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1280-_catalogue_medicaments_ajouter_.png` |
| / | stock | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1920-_.png` |
| /catalogue/medicaments/ | stock | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1920-_catalogue_medicaments_.png` |
| /stocks/ | stock | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1920-_stocks_.png` |
| /rapports/ | stock | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1920-_rapports_.png` |
| /achats/ | stock | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1920-_achats_.png` |
| /achats/2/ | stock | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1920-_achats_2_.png` |
| /achats/2/reception/ | stock | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1920-_achats_2_reception_.png` |
| /stocks/2/inventaire/ | stock | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1920-_stocks_2_inventaire_.png` |
| /catalogue/medicaments/ajouter/ | stock | 1920 | Sans | Sombre | OK | `/tmp/pharmagest-ux-report-uwt80wl_/stock/dark-sans-js-1920-_catalogue_medicaments_ajouter_.png` |

</details>

### Provenance des fichiers

- `/tmp/pharmagest-ux-report-uwt80wl_/summary.json` — SHA-256 `ca4874b1276662a83e834706bd44b7c830e1b0dacee1ab67fdeee0cd6f678ec7`.
- `/tmp/pharmagest-ux-report-uwt80wl_/administrateur/matrix.json` — SHA-256 `b5994801bb33e21ad92a75e7604a8f9686ca16119be9d049b54b715026a6e777`.
- `/tmp/pharmagest-ux-report-uwt80wl_/caissier/matrix.json` — SHA-256 `62973d3423ad8325fa047b006f6790676a3faf709e1c3bf0f168fd0dec189f9b`.
- `/tmp/pharmagest-ux-report-uwt80wl_/gestion/matrix.json` — SHA-256 `93d50ab680e8f448debe4e4676aa1715cda9a89e2f3941091cb725dbe74fb0d2`.
- `/tmp/pharmagest-ux-report-uwt80wl_/pharmacien/matrix.json` — SHA-256 `c2adcd4124e182507c5e6e8b238be44e7c68dcc9789cd25bd1aa3da5d2a37a3e`.
- `/tmp/pharmagest-ux-report-uwt80wl_/stock/matrix.json` — SHA-256 `e67b5582b883a45aa14d04867837d05f9dcd416dcadb7a3b673edd6c276df63e`.

Contrôles de non-régression exécutés pour ce checkpoint : 87 tests Django réussis en 157,887 s ; trois tests Python de journalisation/comparabilité réussis ; 12 tests caisse, 9 tests opérations et 5 tests thème réussis ; check Django, aucune différence de migration et diff sans erreur. Rendu serveur supplémentaire après la retouche stocks : un test réussi (2,044 s). Ces vérifications ne remplacent pas la nouvelle capture stocks demandée ci-dessus.

## 2 novembre 2026 — Contrôle stocks et intégration autorisée

Rapport 4_0pr859 vérifié : 144 cas du rôle stock, tous OK après retouche du tableau. Cette réussite automatique ne remplace pas l'examen visuel exhaustif. L'utilisateur autorise maintenant le commit dans fix/recette-frontend puis la fusion dans main, sans demande de push. Tentative git add refusée : .git/index.lock en lecture seule. Aucun commit ni fusion effectué dans le dépôt actif par l'agent ; commandes à exécuter dans le terminal utilisateur.

## 2 novembre 2026 — Lot 3, présentation rendue et impression

La fusion QA est présente dans main à `3b28d08`. Inspection visuelle de la capture stock post-correction à 768 px : noms lisibles. Protocole, inventaire des 43 couleurs littérales et contrôles différés : [RECETTE_PRESENTATION.md](RECETTE_PRESENTATION.md). Nouvelle commande : `.venv/bin/python tools/run_ux_review.py --matrix --presentation --role administrateur`. Tentative locale fkt1jp4z : socket refusée avant serveur, zéro requête ; contrastes rendus et impression **non exécutés**. Les cinq tests de calcul réussis ne constituent pas une recette navigateur. Aucun résultat des 720 cas historiques n’est remplacé par un résultat attendu.

### Rapport présentation kqi1nqyl reçu

176/176 cas administrateur OK, 11 536 mesures de contraste au repos >=4,5:1 (minimum 5,4348), huit contrôles désactivés exclus ; 12 impressions générées et trois PDF d’une page inspectés. Tableau par largeur/JS/thème, limites et empreinte : [RECETTE_PRESENTATION.md](RECETTE_PRESENTATION.md). Les autres rôles et états, le multipage, les PDF ReportLab et le zoom restent à tester. Colonnes Actions vides et liens d’export encore imprimés : amélioration ouverte, sans bloquer l’enregistrement du checkpoint QA.

### Retouches d’impression après bbe1005

Colonnes Actions et invites de téléchargement masquées sur papier par no-print ; assertions d’impression renforcées. 11 tests de présentation et cinq tests JS réussis. Navigateur après correction **non exécuté**, socket refusée (2obe37jh). Lancer `--matrix --presentation` pour les cinq rôles ; les 176 succès antérieurs ne valident pas ces derniers templates. Avant/après dans RECETTE_PRESENTATION.md.

### Rapport cinq rôles 5wjmy_iw reçu et vérifié

**720/720 cas OK** après les retouches papier, 47 038 mesures de contraste au repos >=4,5:1 (minimum 5,4348), 24 contrôles désactivés exclus ; 720 captures et 52 PDF présents. Texte des 52 PDF contrôlé, trois rendus sombres examinés : colonnes Actions et invites PDF retirées. Tous les documents tiennent sur une page ; aucun résultat multipage/ReportLab revendiqué. Bilan par rôle, preuves et empreintes dans [RECETTE_PRESENTATION.md](RECETTE_PRESENTATION.md). Les tests d’états, zoom, authentification/erreurs, lecteur d’écran et chronométrage restent distincts.

## 2 novembre 2026 — Accessibilité complémentaire validée sur l’hôte

Rapport f2gyt6jp inspecté : 112/112 OK, 112 captures, focus actif/contour 3px dans tous les cas ; 1 024 ratios >=4,5 (minimum 5,6320), seize vérifications d’erreurs locales JS, 1 064 HTTP terminés. Deux captures sombres examinées (connexion sans JS 360 et template 500 JS 768). Défaut de contour et faux échec du bouton hidden clos dans le périmètre testé. Zoom réel 200 %, lecteur d’écran, dialogues métier, handlers HTTP réels et liens de réinitialisation restent ouverts. Tableau et empreinte dans RECETTE_PRESENTATION.md. Aucun nouveau test applicatif ni commit/merge/push.

## 3 novembre 2026 — PDF ReportLab et multipage

Lot documenté dans [RECETTE_PDF.md](RECETTE_PDF.md) : onze PDF après correction, 23 pages converties et toutes examinées ; format français, alignement numérique, largeurs et pieds de page corrigés. Trois fixtures de 80 lignes contrôlées sans perte/doublon, en-têtes répétés. Suite complète **90/90 tests Django réussis** avec ReportLab 4.5.1, check et absence de changement de migration vérifiés. Impression physique/fiscalité/balisage PDF non attestés. Aucun commit/merge/push.
