# Caisse — fluidité, contrôles et recette

## Constats et changements

L’examen du parcours et du code a identifié trois frictions : l’écran intermédiaire pour ouvrir une vente anonyme, l’absence de retour explicite après une recherche sans résultat et l’absence d’estimation avant ajout.

| Avant | Après |
|---|---|
| Nouvelle vente → formulaire client facultatif → ouverture | Bouton explicite « Ouvrir une vente comptoir » ; le choix « Avec un client » reste disponible |
| Sélecteur vide après une recherche infructueuse | Message de résultat et action pour retrouver tous les produits |
| Montant visible après ajout seulement | Prix catalogue indicatif, disponible pour ce panier et sous-total de l’ajout estimé |
| Choix FEFO peu explicite sur une quantité répartie | Estimation des lots nécessaires, quantités déjà au panier déduites et alerte de péremption |
| Monnaie calculée avec `Number` | Calcul en centimes `BigInt`, avec distinction « Monnaie à rendre » / « Montant manquant » |
| Saisie manuelle du montant reçu | Bouton facultatif « Montant reçu exact », qui ne coche aucune confirmation |
| Champs électroniques toujours optionnels côté HTML | Référence et vérification exigées localement quand le mode électronique est choisi par un utilisateur habilité |
| Ordonnance contrôlée surtout au refus serveur | Badge sur la ligne et rappel du contrôle lorsqu’un article du panier le requiert |
| F4 dépendant de l’affichage du formulaire d’ajout | F4 disponible aussi pour un compte autorisé à encaisser sans modifier le panier |

Le raccourci comptoir supprime un écran intermédiaire et un clic. Aucun temps réel de vente n’a encore été mesuré : l’objectif des 30 secondes reste à vérifier en situation de recette.

## Règles inchangées

Le raccourci comptoir soumet le formulaire de création de vente existant avec un client vide. Il ouvre uniquement un **brouillon** et conserve le jeton CSRF, la permission d’ajout et la trace de l’auteur. Il ne crée ni paiement ni sortie de stock. Une consultation GET n’ouvre aucune vente.

Les contrôles de stock, de prix appliqué, d’ordonnance et de paiement restent dans les services Django. Le prix indicatif présenté avant l’ajout ne remplace pas le prix enregistré dans la ligne de vente. La validation conserve ensuite ce prix historique.

Les disponibilités sont une photographie des lots exposés à l’ouverture de la page ; elles ne constituent pas une réservation. La quantité déjà présente dans **ce panier** est déduite pour l’estimation. Les autres ventes peuvent modifier le stock entre-temps : le serveur décide toujours si l’ajout et l’encaissement sont possibles.

Un lot explicite ne devient pas silencieusement un autre lot parce que sa quantité est insuffisante. Si l’utilisateur change de médicament, un lot devenu incompatible revient à FEFO avec un message. Le choix FEFO peut se répartir sur plusieurs lots.

Le montant reçu reste une aide facultative de calcul et n’est pas transmis comme montant comptable. Un résultat de monnaie ou un clic sur « Montant reçu exact » ne confirme pas le paiement. Les paiements électroniques exigent toujours la permission et la vérification prévues côté serveur.

## Architecture et fichiers

| Fichier | Responsabilité |
|---|---|
| `templates/includes/new_sale_actions.html` | Actions communes, contrôlées par permission, pour comptoir ou client identifié |
| `templates/pharmacy/dashboard.html`, `sales.html` | Intégration du raccourci comptoir |
| `templates/pharmacy/sale_detail.html` | Résultats, estimation, contrôles et confirmation de vente |
| `pharmacy/templatetags/ui.py` | Widget de présentation ajoutant le prix indicatif à l’option déjà rendue, sans deuxième liste ni nouvelle requête par médicament |
| `static/js/cashier.js` | Focus, F2/F4, disponibilité indicative, choix de paiement et aide à la monnaie |
| `static/js/cashier-math.mjs` | Fonctions pures : espèces, différence et proposition de lots |
| `static/js/app.js` | Interactions communes ; l’ancienne logique de caisse en a été retirée |
| `templates/base.html` | Point d’insertion pour les scripts propres à un écran |
| `static/css/experience.css` | Résultats, estimation d’ajout et aides de paiement |
| `tools/cashier_math.test.mjs` | Douze cas de calcul indépendants du navigateur |
| `tools/ux_browser_check.cjs` | Vérifications navigateur en lecture seule, à exécuter sur un serveur de test |

Le module de caisse n’est chargé que sur la fiche d’une vente. Les ressources restent locales et aucune écriture n’est réalisée par `fetch`. Les scripts n’ajoutent aucune action interdite aux rôles en consultation.

## Vérifications exécutées

- **79 tests Django réussis**, dont huit nouveaux tests de parcours et de présentation de caisse.
- **21 tests de calcul réussis** : douze pour la caisse et neuf pour les opérations précédentes.
- Syntaxe des scripts vérifiée avec Node ; contrôles Django et absence de nouvelle migration vérifiés.
- Empreintes inchangées pour modèles, vues, services métier, formulaires Python et migration initiale.
- Vérification des règles serveur, y compris ordonnance manquante, historique des prix et permissions.

Les tests de calcul couvrent notamment les grands montants exacts, le montant manquant, la répartition FEFO, les dates identiques, les quantités déjà au panier et le choix d’un lot spécifique.

```bash
python manage.py test
node tools/cashier_math.test.mjs
node tools/operation_math.test.mjs
```

## Recette visuelle et clavier à exécuter

Le serveur du terminal utilisateur n’est pas accessible depuis l’environnement de l’agent. Chromium échoue également au démarrage avec `Operation not permitted`. Aucun rendu, aucune capture et aucun chronométrage navigateur ne sont donc présentés comme validés par les tests ci-dessus.

Tester les quatre largeurs **360, 768, 1280 et 1920 px**, avec une base fictive et un compte caissier, puis un compte pharmacien et un compte de consultation.

- [ ] Ouvrir une vente comptoir depuis le dashboard et depuis la liste ; vérifier brouillon et client anonyme.
- [ ] Choisir « Avec un client » ; conserver le parcours de création habituel.
- [ ] Scanner un code-barres puis Entrée ; vérifier la sélection et le focus sur la quantité.
- [ ] Rechercher un nom inexistant ; comprendre le résultat et retrouver tous les produits.
- [ ] Sélectionner un médicament : prix, disponible et estimation mis à jour sans modifier le panier.
- [ ] Saisir une quantité nécessitant deux lots ; retrouver ces lots après l’ajout réel.
- [ ] Choisir un lot précis insuffisant : absence de remplacement silencieux.
- [ ] Revenir à un médicament sans stock disponible : message compréhensible et ajout désactivé.
- [ ] F2 rejoint la recherche ; F4 rejoint le paiement sans l’encaisser ; les raccourcis ne perturbent pas un dialogue ou le menu mobile.
- [ ] Ordonnance requise : badge, rappel et confirmation explicite ; aucune case cochée automatiquement.
- [ ] Espèces : total 15 000,00 Ar, reçu 20 000,00 Ar → monnaie 5 000,00 Ar ; reçu 10 000,00 Ar → montant manquant 5 000,00 Ar.
- [ ] Montant reçu exact : monnaie zéro et confirmation de vente toujours décochée.
- [ ] Paiement électronique : seuls les utilisateurs habilités voient l’option ; référence et vérification nécessaires ; aucun statut confirmé automatiquement.
- [ ] Après une erreur serveur, le focus permet de lire l’erreur et la saisie est récupérable.
- [ ] Après succès, reçu PDF et ouverture d’une nouvelle vente sont accessibles.
- [ ] Sans JS : recherche GET, ajout POST, choix du lot, ouverture comptoir et validation Django restent fonctionnels.
- [ ] Mobile, zoom et noms longs : aucun débordement de page ; total et panier accessibles.

### Script navigateur facultatif

Avec Playwright déjà préparé selon `RECETTE_UX.md`, définir un compte de test et une vente **en brouillon**, contenant du stock encore disponible en dehors du panier :

```bash
export PHARMAGEST_URL=http://127.0.0.1:8001
export PHARMAGEST_SALE_ID=ID_DE_LA_VENTE_FICTIVE
node tools/ux_browser_check.cjs
```

Le script choisit un produit, contrôle l’estimation et une quantité excessive, vérifie F2/F4, la monnaie et les états des paiements. Il ne clique ni sur l’ajout final au panier ni sur l’encaissement. Il capture les quatre largeurs et vérifie aussi le repli sans JS.

### Mesure de temps manuelle

Effectuer cinq ventes fictives simples, d’un article en stock, à partir du bouton d’ouverture comptoir jusqu’à la confirmation d’encaissement. Noter médiane, erreurs, retours arrière et latence réseau. Décrire séparément le temps nécessaire aux contrôles professionnels : ils ne doivent pas être raccourcis pour atteindre un indicateur de vitesse.

Corriger ensuite les frictions réellement observées avant d’étendre les interactions ou de considérer la recette comme terminée.
