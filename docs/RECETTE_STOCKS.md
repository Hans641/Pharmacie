# Stocks et lots — clarification du 30 octobre 2026

## Changements

| Avant | Après | Fichier |
|---|---|---|
| Recherche avec libellé masqué, état accessible par un sélecteur | Libellés visibles et filtres rapides avec état actif ; la recherche est préservée et la pagination réinitialisée | `templates/pharmacy/stock.html`, `templates/includes/stock_status_filters.html` |
| Quantité physique et badges sans explication de leur lien | Mention « Lot épuisé » à zéro, « Exclu de la vente » si lot bloqué/périmé avec quantité positive ; aide native dépliable | `templates/pharmacy/stock.html` |
| Résultats vides génériques | Nombre de lots filtrés, tri annoncé et action « Afficher tous les lots » si filtre actif | `templates/pharmacy/stock.html` |
| Nom du médicament sans accès direct | Lien vers la fiche uniquement avec `view_medicine` ; nom du menu d'action propre à chaque lot | `templates/pharmacy/stock.html` |
| Styles génériques | Espacements, filtres adaptatifs, états actifs avec soulignement et couleur, noms de lot longs sécables | `static/css/app.css` |

Icône d'information locale ajoutée au sprite `templates/includes/icons.svg`. Aucune dépendance, nouvelle requête de vue ou modification de règle métier. Le compte est celui des résultats filtrés, pas une statistique globale. Un lot peut cumuler blocage et péremption. « Disponibles » décrit le filtre de lots existant ; la disponibilité du médicament, l'ordonnance et les autres contrôles de délivrance restent vérifiés à la caisse.

## Conservation des filtres et du tri

Les paramètres GET conservent la recherche et l'état lors de la pagination. Les raccourcis changent uniquement l'état et retirent `page`. Aucun stockage navigateur ni restauration automatique d'une recherche ancienne n'est ajouté. Le tri serveur existant `expires_on, pk` reste inchangé ; aucun tri local limité à la page n'est présenté comme global.

## Recette manuelle à effectuer

Sur une base fictive, aux largeurs 360, 768, 1280 et 1920 px :

- Rechercher un médicament, un code-barres et un lot ; la recherche couvre les résultats serveur, au-delà de la page affichée.
- Changer de filtre rapide après recherche ; vérifier la conservation du terme, le retrait de la pagination et l'état actif souligné.
- Retirer un filtre, puis afficher tous les lots après une recherche sans résultat.
- Vérifier les cumuls bloqué/périmé, bloqué/sous 90 jours, les échéances aujourd'hui/90/91 jours, et les lots épuisés.
- Comparer stock physique et badges ; ne pas confondre péremption valide et autorisation de délivrance.
- Ouvrir l'aide et les actions au clavier, vérifier les focus, les cibles de 44 px et les noms longs en cartes mobiles.
- Sans JavaScript : formulaire GET, raccourcis, aide native, menus d'actions et pagination utilisables.
- Avec `adjust_stock` : accès à l'inventaire ; avec uniquement `view_lot` : nom du médicament sans lien interdit et aucune action d'inventaire ; avec `view_medicine` : fiche accessible.

Les vérifications navigateur restent non attestées : le démarrage de Chrome était bloqué par le bac à sable lors de la dernière tentative. Les tests serveur ne certifient ni le responsive ni WCAG.
