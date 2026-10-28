# Refonte de l’interface PharmaGest

## Périmètre réalisé

La refonte suit l’audit validé dans `AUDIT_UX.md`. Elle touche les templates, ressources statiques et helpers de présentation. Les fichiers `models.py`, `views.py`, `services.py`, `forms.py` et la migration initiale ont été comparés par empreinte SHA-256 avant/après : ils sont inchangés. Les routes, les champs des transactions, les contrôles de permissions et les validations serveur restent les mêmes.

Les helpers de `pharmacy/templatetags/ui.py` ne font aucune requête de base de données. Ils formatent les valeurs, regroupent les champs et produisent les composants de présentation. Les listes et sélecteurs affichent uniquement les objets déjà exposés par les vues/formulaires existants.

## Design system

### Tokens et conventions

| Domaine | Choix |
|---|---|
| Vert principal / interaction | `#126749` ; survol `#0c4935` |
| Texte / secondaire | `#182d25` / `#52675d` |
| Surfaces | `#ffffff`, fond `#f4f7f5`, surface secondaire `#edf4ef` |
| Succès | texte `#175d3b`, fond `#e6f4eb` |
| Alerte | texte `#784500`, fond `#fff2d9` |
| Danger | texte `#a12727`, fond `#fff0ef` |
| Information | texte `#18567e`, fond `#e9f3fb` |
| Focus | contour 3 px `#1759bd`, décalage 3 px |
| Typographie | Police système locale ; corps 16 px ; secondaire 14 px ; titres 20/24/32 px ; total caisse jusqu’à 48 px |
| Espacement | 4/8/12/16/24/32 px |
| Rayons | 6/8/12 px selon le composant |
| Plans | contenu, éléments collants 20, menus d’en-tête 30, navigation mobile 50 ; dialog natif dans la couche supérieure du navigateur |
| Nombres | Chiffres tabulaires ; alignement à droite ; montant français, par exemple `15 000,00 Ar` |

Ratios calculés : texte principal sur blanc **14,57:1**, secondaire **6,07:1**, bouton primaire **6,86:1**, succès **6,94:1**, alerte **7,15:1**, danger **6,69:1**, information **6,99:1**. Ces mesures concernent ces paires de couleurs ; elles ne remplacent pas une recette de tous les états et ne constituent pas une certification WCAG.

Le thème reste clair pour cette version, conformément au périmètre validé. Un thème sombre complet est différé plutôt que livré sans vérification de tous ses états.

### Composants

Boutons primaire, secondaire, danger et ghost ; champs avec aide/erreur associées ; cases et radios avec libellés tactiles ; badges texte + SVG ; cartes KPI ; tableaux à en-têtes collants et chiffres alignés ; cartes mobiles ; alertes ; résumé d’erreurs focalisable ; menus de ligne HTML natifs ; pagination ; fil d’Ariane ; fenêtre de confirmation native ; région de chargement des recherches.

Les cibles sont dimensionnées à 44 px minimum, y compris les libellés associés aux cases/radios. Les SVG décoratifs portent `aria-hidden`. La navigation utilise `aria-current`, un lien d’évitement et des repères explicites. Les messages d’erreur sont annoncés, les succès utilisent une région de statut.

Aucun squelette permanent n’est affiché : les pages sont rendues côté serveur. Pendant les recherches progressives, un message visible et `aria-busy` signalent le chargement réel. Le bouton de soumission passe en état désactivé après validation native ; un second événement de soumission est ignoré. L’idempotence demeure une responsabilité du serveur.

### Ressources et performance

- Bootstrap **5.3.8**, copié depuis une distribution déjà présente localement, conserve son en-tête de version et sa licence MIT dans `static/css/vendor/`.
- Aucune police distante ; SVG inline regroupés en un sprite commun.
- JavaScript vanille local, différé ; aucun framework ni étape de build.
- CSS métier environ 26 Ko, JS environ 12 Ko, Bootstrap environ 232 Ko avant compression. Prévoir cache et compression des statiques au déploiement.
- Les photos des listes ont des dimensions réservées et un chargement différé.

## Changements fichier par fichier

| Fichier | Avant | Après |
|---|---|---|
| `templates/base.html` | Structure monolithique, Bootstrap CDN, glyphes | Structure courte, includes, ressources locales, lien d’évitement et région d’annonce |
| `templates/includes/navigation.html` | Menu dans `base.html`, actif uniquement au tableau de bord | Navigation par famille de routes, permissions existantes, support tiroir mobile |
| `templates/includes/nav_item.html` | Aucun composant | Lien avec SVG et `aria-current` |
| `templates/includes/header.html` | Faux fil d’Ariane, actions de compte éparses | Fil d’Ariane navigable, menu de compte natif, commande du tiroir |
| `templates/includes/icons.svg` | Glyphes dépendants des polices | Sprite SVG cohérent, sans téléchargement |
| `templates/includes/messages.html` | Tous les messages en alerte urgente | Erreur en alerte, succès en statut, icône complémentaire |
| `templates/includes/field.html` | Champ rendu dans `form.as_p` | Libellé, indication obligatoire, aide et erreurs associées ; affichage du mot de passe |
| `templates/includes/form_fields.html` | Formulaire non structuré | Sections et grille responsive, champs cachés conservés |
| `templates/includes/form_errors.html` | Erreurs dispersées | Résumé focalisable avec liens vers les champs |
| `templates/includes/filter_chips.html` | Filtres peu visibles après soumission | Filtres actifs et retrait individuel préservant les autres paramètres |
| `templates/includes/lot_status.html` | Un seul état « valide/périmé/bloqué » | Péremption et blocage affichés séparément avec icône et texte |
| `templates/includes/document_status.html` | Badges neutres et répétés | États homogènes des ventes et commandes |
| `templates/includes/confirm_dialog.html` | Pas de confirmation progressive commune | Dialog natif pour les formulaires explicitement marqués |
| `templates/pharmacy/sale_detail.html` | Recherche sous le panier, paiement en liste, fin de vente sans enchaînement | Recherche en tête, parcours clavier, aide FEFO, total dominant, radios tactiles, monnaie indicative, reçu et nouvelle vente |
| `templates/pharmacy/dashboard.html` | Grand bandeau décoratif, urgences plus bas | Alertes en tête, accès rapides par rôle, KPI, classement graphique léger sur données réelles |
| `templates/pharmacy/stock.html` | Tableau défilant, états incomplets | Cartes mobiles, filtres visibles, états complets, menu d’action natif |
| `templates/pharmacy/entity_list.html` | Prix anglais préformaté, petites actions, tri parfois mal réaffiché | Prix rendu depuis le décimal de l’objet, état du tri conservé, filtres/chips, cartes mobiles et actions regroupées |
| `templates/pharmacy/form.html` | Formulaire générique et bouton « Enregistrer » | Sections, texte d’action spécifique, contexte réception/inventaire/retour et actions collantes sur mobile |
| `templates/pharmacy/confirm.html` | Titre « Archiver / supprimer » ambigu | Vocabulaire spécifique : supprimer une catégorie ou archiver une fiche |
| `templates/pharmacy/purchase_detail.html` | Champs en paragraphes et total peu distinct | Composants de formulaire, montants français, cartes mobiles, confirmation d’annulation progressive |
| `templates/pharmacy/purchases.html` | Liste dense | Lisibilité commune, recherche progressive, chips, cartes mobiles et états homogènes |
| `templates/pharmacy/sales.html` | Liste dense | Montants français, recherche progressive, états homogènes et cartes mobiles |
| `templates/pharmacy/detail.html` | Valeurs brutes, prix sans format homogène | Décimaux monétaires et booléens lisibles, états des lots, historique homogène |
| `templates/pharmacy/movements.html` | Tableau dense | Recherche progressive, cartes mobiles et variation alignée |
| `templates/pharmacy/audit.html` | Tableau dense | Recherche progressive, filtres visibles et cartes mobiles |
| `templates/pharmacy/users.html` | Petits liens ; lien de modification du superadministrateur visible aux administrateurs métier | Cartes mobiles ; lien masqué lorsque la vue le refuserait déjà |
| `templates/pharmacy/reports.html` | Glyphes et petits textes | Icônes SVG et cartes cohérentes, impression dédiée |
| `templates/pharmacy/pagination.html` | Petits boutons | Navigation nommée, cibles tactiles et conservation des paramètres GET |
| `templates/registration/login.html` | Formulaire brut et style inline | Connexion sobre, composants de champs, affichage/masquage du mot de passe |
| `templates/registration/password_change_form.html` | `form.as_p` | Champs accessibles et erreurs structurées |
| `templates/registration/password_reset_form.html` | `form.as_p` | Champs accessibles et erreurs structurées |
| `templates/registration/password_reset_confirm.html` | `form.as_p` | Champs accessibles, mot de passe affichable et erreurs structurées |
| `templates/registration/password_change_done.html` | Glyphe de marque | Marque SVG et styles communs |
| `templates/registration/password_reset_done.html` | Glyphe de marque | Marque SVG et styles communs |
| `templates/registration/password_reset_complete.html` | Glyphe de marque | Marque SVG et styles communs |
| `templates/403.html` | Glyphe de marque | SVG et styles communs |
| `templates/404.html` | Glyphe de marque | SVG et styles communs |
| `templates/500.html` | Glyphe de marque | SVG et styles communs |
| `static/css/app.css` | CSS comprimé, textes jusqu’à 8 px | Tokens et composants commentés, base 16/14 px, responsive 360–1920 ciblé |
| `static/css/print.css` | Quelques règles dans le CSS principal | Feuille d’impression dédiée, structure tabulaire restaurée, contrôles masqués |
| `static/css/vendor/bootstrap.min.css` | CDN | Distribution locale avec licence |
| `static/js/app.js` | Aucun JS | Tiroir, focus, raccourcis, monnaie indicative, confirmation, verrouillage et recherche GET progressive |
| `pharmacy/templatetags/ui.py` | Aucun helper UI | Présentation sans mutation ni requête : montants, dates, champs et navigation |
| `pharmacy/test_ui.py` | Aucun test spécifique de présentation | Contrats HTML, montants, états, permissions des actions et contexte des opérations |
| `tools/ux_browser_check.cjs` | Aucun contrôle navigateur reproductible | Script Playwright facultatif : 360/768/1280/1920, captures, débordements, cibles, tiroir, monnaie et repli sans JS |

Les courriels de réinitialisation, les PDF générés côté serveur et les mentions métier ne sont pas modifiés.

## Caisse : comportement précis

- F2 rejoint la recherche ; Entrée lance sa recherche GET. Un code-barres exact est déjà présélectionné par la vue existante ; avec JS, un résultat unique est également présélectionné, puis la quantité reçoit le focus.
- Entrée depuis la quantité soumet l’ajout au panier. Aucune recherche ne déclenche automatiquement l’encaissement.
- Le lot avancé reste facultatif. La suggestion se base sur les lots exposés par le formulaire et déduit les quantités déjà dans le panier ; le serveur garde le contrôle FEFO et de disponibilité.
- F4 rejoint l’encaissement sans le valider. Les modes électroniques n’apparaissent qu’aux utilisateurs possédant déjà `verify_payment`.
- La monnaie est calculée en centimes, accepte virgule ou point et ne constitue pas un nouveau champ comptable. Un montant insuffisant est signalé ; cette aide ne remplace pas le contrôle professionnel du paiement.
- Après validation, le reçu PDF et la facture restent disponibles. L’impression HTML est distincte du téléchargement PDF. La nouvelle vente et le retour sont affichés selon leurs permissions.

## Limites assumées

Pas de pourcentages de tendance inventés, de tri global de stock supplémentaire ou de mutation en masse. Les filtres persistent dans l’URL et la pagination ; aucune donnée client n’est conservée dans localStorage. Aucune vente hors ligne. La recherche progressive reste un GET serveur et son bouton natif fonctionne sans JS. Le nombre de requêtes HTTP de recherche augmente avec l’usage ; une temporisation de 450 ms et l’annulation des requêtes précédentes limitent les appels.

Les quatre tailles ont un plan et un script de recette, mais leur validation visuelle effective nécessite un navigateur autorisé. Le lancement de Chromium dans l’environnement de travail a échoué avec `Operation not permitted` ; aucune capture ni conformité navigateur n’est revendiquée sur la base des seuls tests Django.
