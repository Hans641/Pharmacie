# Parcours opérationnels : réception, inventaire et retour

Cette itération poursuit l’interface sans transformer les opérations fréquentes en assistants à étapes. Chaque opération conserve un seul formulaire et un seul enregistrement final.

## Ce qui change

| Parcours | Avant | Après |
|---|---|---|
| Réception | Liste des reliquats et formulaire générique | Sections Articles reçus / Traçabilité du lot / Confirmation ; valeur de la livraison, unités entrantes et reliquat estimé affichés avant validation |
| Inventaire | Stock initial et formulaire de comptage | Quantité comptée, écart signé et statut de blocage prévus ; confirmation reprenant ces données |
| Retour | Historique de la ligne et champs génériques | Quantité encore retournable, montant exact à consigner et effet sur le stock ; avertissement explicite si la réintégration est impossible |
| Confirmation | Texte générique | Titre, bouton et récapitulatif adaptés à l’opération ; la couleur ne remplace pas les quantités et libellés |

Les détails des lignes sont consultables dans des sections dépliables HTML. Sans JavaScript, ils restent disponibles, les champs conservent leurs noms et les formulaires restent utilisables. Les récapitulatifs calculés sont masqués jusqu’à leur initialisation, pour ne pas afficher une estimation fictive.

La réception utilise déjà sa case de confirmation et son bouton final ; aucune fenêtre supplémentaire n’est ajoutée. L’inventaire et le retour conservent leur confirmation sensible, avec un texte désormais précis.

## Informations calculées

### Réception

- Ligne sélectionnée et quantité réellement reçue aujourd’hui.
- Valeur des marchandises reçues, calculée au prix historique de la ligne d’achat.
- Reliquat de cette ligne après livraison.
- Nombre d’unités entrantes, sans prétendre connaître le stock total actuel du médicament.
- Quantité maximale issue du reliquat affiché et péremption minimale selon la date du serveur à Madagascar.

Une réception n’est pas présentée comme un paiement fournisseur. Une ligne sans reliquat ne permet pas de saisir une nouvelle entrée. Les réceptions partielles restent gérées par le même service Django.

### Inventaire

- Stock enregistré au chargement, quantité comptée et différence signée (`−3`, `0`, `+2` unités).
- Blocage demandé ou absence de blocage ; l’absence de blocage ne dispense jamais du contrôle de péremption.
- Mention explicite d’un éventuel changement de stock depuis l’ouverture de la page.

La différence affichée est indicative. Le service recalcule la correction sur le stock courant, dans sa transaction.

### Retour

- Quantité encore retournable, après déduction des retours déjà enregistrés.
- Montant au prix effectivement appliqué lors de la vente, sans recalcul avec le prix courant du médicament.
- Réintégration demandée ou absence de remise en stock.
- Signalement du blocage ou de la péremption si la case de remise en stock est cochée.
- Référence du remboursement déjà effectué reprise dans la confirmation.

Décocher la remise en stock permet de consigner un retour sans réintégration, sous réserve des validations serveur. Le logiciel ne déclenche aucun remboursement externe.

## Architecture

| Fichier | Rôle |
|---|---|
| `templates/includes/operation_context.html` | Situation initiale et données des lignes déjà accessibles au formulaire |
| `templates/includes/operation_preview.html` | Récapitulatif réutilisable, initialement masqué |
| `templates/pharmacy/form.html` | Activation selon le parcours, sans changer les URLs ou champs POST |
| `pharmacy/templatetags/ui.py` | Regroupements de présentation, date locale et montants en centimes exacts |
| `static/js/operations.js` | Actualisation du récapitulatif et des contraintes indicatives |
| `static/js/operation-math.mjs` | Calculs purs utilisant `BigInt`, sans flottants ni requêtes réseau |
| `static/js/forms.js` | Messages correctifs lorsque les contraintes locales évoluent |
| `static/js/app.js` | Dialogue commun avec titre, texte et bouton adaptés |
| `static/css/experience.css` | Cartes de contexte et récapitulatifs responsive |

La mise à jour du récapitulatif précède la validation locale et la confirmation. Les messages personnalisés utilisent les mêmes emplacements d’aide inline. Les valeurs provenant des articles ou saisies sont injectées via `textContent`, jamais interprétées comme du HTML.

La date utilisée provient de Django, selon le fuseau configuré, plutôt que de l’horloge du navigateur. Les montants sont transmis sous forme de chaînes de centimes, multipliés comme entiers `BigInt`, puis formatés en français. Les mêmes calculs restent exacts au-delà de la précision entière de `Number`.

Aucun modèle, service métier, formulaire Python, vue, permission ou migration n’est modifié. Aucun brouillon n’est enregistré par JavaScript. Les informations exposées proviennent uniquement du formulaire déjà autorisé par la vue.

## Vérifications

Résultat de cette itération : **71 tests Django et 9 tests de calcul réussis**. Les contrôles de syntaxe JavaScript, `manage.py check`, `makemigrations --check --dry-run` et `git diff --check` passent. Les empreintes des modèles, vues, services, formulaires Python et migration initiale sont inchangées.


Calculs indépendants du navigateur :

```bash
node tools/operation_math.test.mjs
```

Les neuf cas couvrent : entiers et valeurs ambiguës, très grands montants, quantités signées, inventaire nul ou sans écart, livraison partielle, plafond de retour, grande multiplication et éligibilité à la remise en stock.

Tests Django :

```bash
python manage.py test
```

Les tests supplémentaires vérifient notamment les reliquats réels, la conservation des champs et jetons, l’absence de données d’opération pour les rôles non autorisés et les refus serveur d’une réception ou d’un retour excessif sans JavaScript.

## Recette navigateur à compléter

Le serveur lancé depuis le terminal utilisateur n’est pas accessible depuis l’environnement de l’agent. Les vérifications HTML et de calcul ne remplacent donc pas cette recette visuelle.

Le script `tools/ux_browser_check.cjs` reconnaît les trois formulaires lorsque leurs URLs sont ajoutées à `UX_ROUTES`. Il remplit uniquement des valeurs de recette, observe les récapitulatifs et n’active aucun bouton d’enregistrement final.

Exemple, avec les identifiants d’une base fictive et le compte Playwright préparé selon `RECETTE_UX.md` :

```bash
export PHARMAGEST_URL=http://127.0.0.1:8001
export UX_ROUTES=/stocks/1/inventaire/,/achats/2/reception/,/ventes/3/retour/
node tools/ux_browser_check.cjs
```

Utiliser une commande avec reliquat positif et une vente comportant encore une quantité retournable. Adapter les URLs aux objets réels et aux permissions du compte de test.

À contrôler à 360, 768, 1280 et 1920 px :

- [ ] Sélectionner une ligne : montant, reliquat et effet sur le stock cohérents.
- [ ] Saisir une quantité excessive : indication corrective avant enregistrement.
- [ ] Réceptionner 8 unités sur 20 : reliquat estimé 12 ; stock réel augmenté de 8 après confirmation.
- [ ] Compter 17 pour un stock affiché de 20 : correction estimée de −3 ; motif conservé après enregistrement.
- [ ] Changer le blocage : statut prévu explicite, pas d’assimilation « non bloqué » à « délivrable ».
- [ ] Retourner 2 unités vendues 1 500,00 Ar : remboursement à consigner de 3 000,00 Ar.
- [ ] Choisir un lot bloqué ou périmé puis demander la remise en stock : message explicite ; décocher permet de poursuivre sans réintégration.
- [ ] Modalité de confirmation : titre, montant/quantité et référence exacts ; Échap annule et restitue le focus.
- [ ] Sans JS : contexte accessible et validations Django inchangées.
- [ ] Lecteur d’écran : les messages ne se répètent pas lorsque leur contenu reste identique.
