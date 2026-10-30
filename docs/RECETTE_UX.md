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
