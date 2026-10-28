# Audit UX de PharmaGest — étape 1

Date : 28 octobre 2026. Périmètre : les 27 templates HTML, les deux templates de courrier, l’intégralité de `static/css/app.css`, puis les formulaires et les contextes des vues nécessaires pour vérifier la faisabilité. Aucun template, style ou traitement métier n’a été modifié à cette étape.

Cet audit repose sur le code. Les ratios ci-dessous sont calculés à partir des couleurs CSS, et non mesurés sur des captures. Il ne constitue ni une certification WCAG ni une recette visuelle. Les comportements du navigateur, le chronométrage au comptoir et les quatre largeurs cibles restent à tester.

## Résultat

La structure métier est exploitable, mais la présentation ralentit les tâches et rend certains états difficiles à distinguer. Priorités : lecture des données essentielles, caisse au clavier, séparation explicite des états, navigation mobile et erreurs de formulaire.

Effort relatif : **S** = correction localisée ; **M** = composant et plusieurs écrans ; **L** = parcours complet, interaction et recette. Ces estimations ne sont pas des délais garantis.

## Audit priorisé

| Priorité | Problème observé et emplacement | Impact | Correctif proposé | Effort |
|---|---|---|---|---|
| Critique | Textes à 8–13 px dans `app.css` ; tableaux à 12 px, en-têtes à 9 px, liens d’action à 11 px | Lecture lente au comptoir, erreurs de quantité et fatigue | Texte courant 16 px, texte secondaire au moins 14 px ; chiffres tabulaires ; largeur et hauteur de ligne suffisantes | M |
| Critique | Contrastes faibles des textes, aides et badges | États et données difficiles à lire | Tokens de couleurs vérifiés sur leurs fonds réels ; objectif 4,5:1 pour le texte courant | M |
| Critique | Liens d’action sans surface tactile garantie, boutons secondaires/pagination petits | Mauvaises activations sur tablette et téléphone | Cibles d’au moins 44 × 44 px, espacement entre actions et focus renforcé | M |
| Critique | Caisse : recherche après le panier, plusieurs sélecteurs, absence d’autofocus et de raccourcis | Parcours fragmenté ; objectif des 30 secondes non démontré | Recherche/scan en tête, boucle clavier recherche → quantité → ajout, lot FEFO avancé et panier facilement accessible | L |
| Critique | Encaissement : aucun calcul de monnaie, paiement dans un petit sélecteur, total 31 px, pas de protection visuelle contre les doubles clics | Hésitation et risque de mauvaise manipulation malgré l’idempotence serveur | Total dominant, choix radio sous forme de grandes cibles, calcul indicatif de monnaie pour les espèces, bouton occupé après validation HTML | L |
| Critique | Navigation mobile : tous les liens s’empilent ; tableaux défilants ; aucune stratégie mobile pour la caisse | Le contenu utile est repoussé et la comparaison des lignes devient difficile | Tiroir mobile progressif ; lignes en cartes avec libellés ; résumé du panier/total et accès à l’encaissement persistants | L |
| Important | Focus seulement partiel ; absence de lien d’évitement et de `aria-current` ; colonne d’action parfois sans intitulé | Repérage clavier et lecteur d’écran incomplet | Lien « Aller au contenu », repères sémantiques, focus visible sur chaque contrôle, intitulés et état actif | M |
| Important | Lots proches de péremption présentés comme « Valide » ; périmé/bloqué fusionnés dans un seul affichage | L’utilisateur ne distingue pas toutes les précautions utiles | États explicites avec icône et texte ; afficher séparément le blocage et la péremption si les deux s’appliquent | M |
| Important | Formulaires génériques `form.as_p`, aucun regroupement métier ni résumé d’erreurs | Recherche des champs et correction coûteuses | Includes de champ avec libellé, aide et erreurs associées ; sections ; deux colonnes sur grand écran ; résumé d’erreurs avec liens | L |
| Important | Réception : formulaire générique, quantité et reliquat peu contextualisés | Risque de confusion entre commandé, reçu et à recevoir | Étapes visuelles, rappels des données disponibles, libellés « Quantité reçue aujourd’hui » et confirmation de l’effet sur le stock | M |
| Important | Inventaire : « Enregistrer » ne décrit pas la correction ; blocage dans le même formulaire | Conséquence de l’opération peu anticipable | Afficher le stock avant comptage, expliquer la différence et le blocage, bouton « Confirmer l’inventaire » | M |
| Important | Retour : remise en stock et remboursement présentés comme des champs ordinaires | Confusion possible entre enregistrer un remboursement déjà réalisé et le déclencher | Sections « Produit retourné », « Éligibilité », « Remboursement effectué » et récapitulatif avant confirmation | M |
| Important | Après vente : lien « Reçu PDF », aucune action « Nouvelle vente » dans la confirmation | Enchaînement au comptoir ralenti | Confirmation persistante avec référence, montant, accès au PDF et nouvelle vente selon permission | M |
| Important | Seul le tableau de bord reçoit `selected` ; fil d’Ariane décoratif et non navigable | Perte de repère dans les fiches et sous-pages | Navigation active par famille de routes et catégorie de catalogue, fil d’Ariane en `<nav>` | M |
| Important | Bandeau décoratif haut de 190–210 px ; alertes sous les analyses | Urgences moins visibles | Retirer le bandeau ; alertes actionnables en premier ; accès rapides selon rôle ; puis indicateurs et analyses | M |
| Important | Filtres sans chips, tri du catalogue réaffiché incorrectement pour certains choix ; stocks sans tri proposé | État de recherche ambigu, répétition de manipulations | URL GET conservée, filtres actifs avec retrait individuel, réinitialisation ; tri serveur conservé là où il existe | M |
| Important | Prix catalogue déjà transformés en texte anglais dans le contexte (`1,500.00 Ar`) | Format monétaire non homogène | Rendre le prix décimal de l’objet dans le template et utiliser un formateur de présentation français unique ; ne pas changer le calcul métier | M |
| Important | Messages tous en `role="alert"`, absence de résumé clair après erreur et de focus sur celui-ci | Interruptions excessives ou erreurs difficiles à retrouver | Succès dans une région de statut, erreurs annoncées et résumé focalisable ; conserver les saisies | M |
| Important | Bootstrap chargé depuis un CDN | Dépendance externe et coût de connexion sur première visite | Copier la distribution officielle de Bootstrap en local avec sa licence et sa version ; aucun chargement réseau pour l’interface | S |
| Confort | Glyphes Unicode hétérogènes et répétés pour des fonctions distinctes | Reconnaissance visuelle incertaine selon la plateforme | Sprite SVG local cohérent ; icônes décoratives masquées aux lecteurs d’écran ; libellés explicites | M |
| Confort | `base.html` monolithique, champs et messages répétés, style inline de connexion, CSS comprimé | Corrections incohérentes et maintenance difficile | Partials navigation, en-tête, messages, champs, états vides et pagination ; CSS organisé et commenté | M |
| Confort | Connexion sans affichage du mot de passe | Erreurs de saisie sur mobile | Bouton accessible afficher/masquer, autocomplétion appropriée, erreur générale courte | S |
| Confort | Impression limitée à masquer quelques éléments | Coupures et colonnes inutiles possibles | Feuille d’impression locale : contraste noir/blanc, lignes et en-têtes répétés, suppression des contrôles ; lien PDF explicite | M |
| Confort | Pas d’état de chargement des listes | Incertitude sur connexion lente si une recherche progressive est ajoutée | Indicateur discret et `aria-busy` pendant une requête ; squelettes uniquement pour un chargement réel | S |

## Contrastes calculés sur les couleurs existantes

| Usage | Texte / fond | Ratio | Cible du projet pour le texte courant |
|---|---|---:|---|
| Texte atténué sur blanc | `#78878c` / `#ffffff` | 3,72:1 | Insuffisant |
| En-têtes de tableau | `#91a096` / `#fafcfb` | 2,66:1 | Insuffisant |
| Compléments KPI | `#96a198` / `#ffffff` | 2,68:1 | Insuffisant |
| Badge alerte | `#ab7c31` / `#fcf2df` | 3,34:1 | Insuffisant |
| Badge succès | `#278365` / `#e7f5ed` | 4,13:1 | Insuffisant |
| Vert principal sur blanc | `#14795d` / `#ffffff` | 5,35:1 | Suffisant pour cette paire |

Il faut vérifier également focus, bordures utiles, survol, désactivation, surfaces colorées et éventuel thème sombre. L’existence d’un token conforme ne suffit pas à garantir tous les écrans.

## Direction du design system à valider

- Une interface métier sobre : vert principal, surfaces neutres, sémantique succès/alerte/danger/information. Les états portent toujours un texte, avec une icône complémentaire.
- Police système locale, sans téléchargement : privilégier lisibilité et disponibilité immédiate. Aucune police distante n’est actuellement chargée ; `Inter` n’est qu’un nom dans la pile de polices.
- Corps 16 px ; secondaire 14 px ; titres 20/24/32 px ; montant principal de caisse 40–48 px selon largeur. Espacements 4/8/12/16/24/32 px.
- Boutons et champs hauts d’au moins 44 px ; focus à fort contraste ; nombres alignés à droite avec chiffres tabulaires.
- CSS lisible séparé en tokens, base, structure, composants, écrans et impression. Bootstrap local reste une fondation, les composants métier ont des règles explicites.
- Navigation desktop fixe, tiroir mobile avec fermeture clavier et restauration du focus. Sans JavaScript, la navigation reste accessible par un mécanisme HTML natif.
- Mode clair prioritaire. Un mode sombre automatique ne sera ajouté que si les mêmes vérifications de contraste et d’états peuvent être réalisées ; sa présence n’est pas un prérequis à la première itération.

## Parcours cible de caisse

1. Ouvrir une vente, avec ou sans client.
2. Placer le focus dans « Rechercher ou scanner un médicament ».
3. Rechercher/scanner, saisir la quantité et ajouter avec Entrée. Le lot automatique reste FEFO ; les choix avancés ne surchargent pas le parcours courant.
4. Garder le panier et son montant accessibles. Signaler tout lot proche de péremption dans la ligne correspondante.
5. Choisir le paiement par de grandes cibles. Pour les espèces, afficher la monnaie indicative à partir d’un montant reçu ; ne pas transmettre cette aide comme une nouvelle opération comptable.
6. Confirmer explicitement l’encaissement. Aucun raccourci de recherche ne doit déclencher seul une vente.
7. Afficher le succès et proposer le reçu PDF et la nouvelle vente uniquement aux rôles autorisés.

L’objectif de moins de 30 secondes doit être chronométré sur une vente simple, puis décrit avec ses conditions : nombre de produits, état initial et latence. Il ne peut pas être garanti par un examen du code.

## Périmètre sans modification métier

Les templates, CSS, SVG et JavaScript progressif suffisent pour l’essentiel. Des helpers de présentation Django pourront servir à formater les montants et classer les dates sans changer les modèles, les vues ou les règles métier. Ils ne doivent pas interroger la base ni décider si une transaction est autorisée.

Les formulaires POST, champs, jetons CSRF et conditions de permissions restent inchangés. Les confirmations HTML restent utilisables sans JavaScript. La désactivation d’un bouton intervient après la validation du formulaire et préserve le champ `action` transmis ; elle est réinitialisée au retour navigateur. Le JavaScript ne prétend pas garantir l’idempotence, déjà assurée côté serveur.

La recherche progressive doit réutiliser les recherches serveur GET existantes, conserver la pagination et gérer les réponses arrivant dans le désordre. Un filtrage sur 15 lignes visibles ne sera jamais présenté comme une recherche dans tout le catalogue. Les préférences de filtre ne doivent pas conserver de données clients sensibles dans le stockage du navigateur.

## Demandes qui dépassent une refonte strictement visuelle

| Demande | Limite constatée | Proposition pour la première version |
|---|---|---|
| Tendances KPI | Le contexte ne contient pas la période précédente ni les séries quotidiennes | Ne pas inventer de pourcentage ou de courbe temporelle ; graphiques de classement possibles avec les données déjà disponibles. Une évolution ultérieure pourra ajouter les agrégations aux vues |
| Tri global des stocks | La vue ne traite pas de paramètre de tri | Conserver l’ordre serveur FEFO ; tout tri local doit être explicitement limité à la page courante. Ajouter le tri global uniquement dans une évolution autorisée de la vue |
| Filtres ruptures / stocks faibles | Le catalogue propose un tri de stock, mais pas de filtre seuil/rupture | Liens vers le tri existant, avec un libellé exact ; ne pas présenter ce lien comme une liste filtrée exhaustive |
| Actions en masse | Aucun contrat serveur de mutation en masse | Reporter les mutations en masse ; ne pas multiplier silencieusement des requêtes POST dans le navigateur |
| Imprimer directement un PDF | Le serveur le livre en pièce jointe ; comportement dépendant du navigateur | Action « Télécharger le reçu PDF » claire, impression via le lecteur PDF ; impression HTML distincte si utile, sans prétendre ouvrir automatiquement la boîte d’impression PDF |
| Validation en ligne | Les règles métiers complètes appartiennent au serveur | Contrôles HTML et aide immédiate pour les erreurs simples ; le serveur conserve la décision finale |
| Mode hors ligne | Les ventes exigent un état de stock serveur fiable | Ressources statiques locales ; aucune vente hors ligne ni paiement simulé |

## Itérations et critères de sortie

1. **Audit → validation de ce périmètre.** Aucun écran modifié avant cette étape.
2. **Design system et structure.** Tokens, composants, icônes et ressources locales ; vérifier navigation clavier et styles de base.
3. **Caisse.** Boucle scan/quantité/ajout, panier, encaissement, monnaie indicative, succès et raccourcis documentés ; vérifier sans JS et selon permissions.
4. **Tableau de bord.** Alertes prioritaires et accès rapides par rôle, analyses honnêtes sur les données disponibles.
5. **Stocks et lots.** États distincts, filtres, menus de ligne et affichage mobile.
6. **Listes et formulaires.** Composants communs, cartes mobiles, erreurs, réception, inventaire, retours et connexion.
7. **Recette.** Tests Django existants, contrôles de rendu/permissions nécessaires aux changements et recette navigateur aux largeurs 360, 768, 1280 et 1920 px. Rapporter les vérifications réellement exécutées et toute limitation de l’environnement.

Chaque itération documentera les fichiers touchés et les changements avant/après. Le bilan final comprendra la checklist UX/accessibilité, le plan de test par rôle et les évolutions différées.

## Plus tard

Tendances globales calculées côté serveur, tri serveur supplémentaire, mutations en masse avec prévisualisation, lecture caméra de codes-barres, raccourcis personnalisables et éventuel mode hors ligne conçu avec une stratégie de synchronisation et de résolution des conflits de stock.
