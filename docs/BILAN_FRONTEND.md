# Bilan de recette frontend — 4 novembre 2026

PharmaGest : Django/templates, ressources locales et JS progressif. Ce bilan distingue les preuves automatisées, l’inspection visuelle et les confirmations utilisateur. Il ne constitue pas une certification WCAG, fiscale ou d’exploitation.

## Périmètre livré

Design system, navigation/mobile, tableaux et listes, formulaires guidés, prévisualisations d’opérations, caisse/FEFO/monnaie/raccourcis, dashboard/stock clarifiés, thèmes système/clair/sombre, métadonnées/favicon local et impressions/PDF. Les permissions et calculs métier ont été conservés. Les fonctionnalités optionnelles nécessitant des vues nouvelles restent reportées.

## Tableau des preuves acquises

| Contrôle | Résultat réellement vérifié | Preuve détaillée |
|---|---|---|
| Matrice cinq rôles × 4 largeurs × 2 thèmes × JS/sans JS | 720/720 OK ; 47 038 mesures de contraste au repos >=4,5 ; 24 contrôles désactivés exclus | RECETTE_PRESENTATION, rapport 5wjmy_iw |
| Connexion, reset et templates d’erreur | 112/112 OK ; 1 024 mesures de contraste, focus 3 px | RECETTE_PRESENTATION, f2gyt6jp ; templates d’erreur isolés, pas handlers HTTP réels |
| Doubles activations, retour navigateur et rejeu | 12/12 OK ; paiements/mouvements uniques, stocks conformes | RECETTE_CAISSE, v2a883_n |
| Chronométrage automatisé | 15/15 OK ; médianes simple 2,126 s / trois produits 4,345 s / ordonnance 2,082 s | RECETTE_CAISSE, didge5bc ; fin à confirmation HTML, PDF exclu |
| Documents ReportLab | 11 PDF, 23 pages converties et toutes inspectées ; trois fixtures de 80 lignes conservées intégralement | RECETTE_PDF, ia7_9zpz |
| Tests Django avec ReportLab (3 novembre) | 90/90 réussis, 157,198 s | RECETTE_PDF et mémoire ; environnement propre temporaire |
| Parcours HTTP de rôle/CSRF | 15/15 OK ; cinq positifs, neuf refus sans mutation et un refus CSRF | RECETTE_ROLES, p9de2osq ; client Django, pas navigateur |
| Parcours manuels des cinq rôles | OK déclaré par l’utilisateur le 4 novembre | RECETTE_ROLES ; versions/dimensions/captures non fournies |
| Zoom/clavier antérieur | Trois parcours signalés réglés par l’utilisateur | RECETTE_ZOOM_CLAVIER ; pas d’extrapolation aux combinaisons non attestées |

Les rapports sous /tmp sont des artefacts temporaires. Les guides gardent résultats et empreintes ; leur chemin ne garantit pas qu’ils survivent à un redémarrage.

## Défauts corrigés avec cause identifiée

- Clic de période sans JS : condition hors écran/smooth isolée ; surcharge du scroll Bootstrap, comparaison de 0/20 à 20/20 réussites.
- Tableaux comprimés sur tablette : largeur minimale et défilement interne, après inspection des noms morcelés malgré une géométrie automatique OK.
- Focus de bouton : outline Bootstrap plus spécifique que le sélecteur global ; règle ciblée et mesure de 3 px.
- Soumission caisse : champ name=method masquant form.method ; accès par getAttribute, test reproduisant le TypeError puis recette navigateur conforme.
- PDF : formats anglais, alignement, colonnes et page de mention légale seule ; présentation commune corrigée, tests du texte et inspection de toutes les pages générées.

Les faux échecs d’outillage (bouton hidden sélectionné, navigation retenue et attente circulaire, type de mouvement inventaire incorrect) sont documentés dans leurs guides ; ils ne sont pas comptés comme défauts métier corrigés.

## Limites restantes et priorités

1. Compléter le lecteur d’écran et l’ordre complet du clavier, ainsi que les combinaisons de zoom/texte seul non attestées. Aucun statut AA global acquis.
2. Mesurer humainement les trois scénarios de vente, cinq passages chacun. Les médianes Playwright ne mesurent pas les contrôles professionnels réels.
3. Vérifier impression physique/thermique et documents réels dans le cadre prévu ; la conformité fiscale des mentions n’est pas établie.
4. Tester si nécessaire les handlers HTTP réels d’erreur et les liens de reset valides/invalides ; les captures de templates isolés ne les prouvent pas.
5. Préparer l’exploitation selon EXPLOITATION.md si le projet doit être déployé : cette étape dépasse la recette d’interface.

Aucun défaut bloquant supplémentaire signalé lors de la confirmation des parcours. Les points non exécutés ci-dessus restent ouverts ; leur absence de défaut mesuré n’est pas une réussite.

## Dépôt et archive

Main vérifié à 60a9aea (fusion caisse/PDF). La recette par rôle, son lanceur et ce bilan constituent des changements non commités ; commit en branche dédiée et fusion main autorisés le 4 novembre ; tentative de création de branche refusée (.git en lecture seule), aucun commit/fusion effectué par l’agent et aucun push autorisé. Les fichiers applicatifs restent sans diff dans ce lot.

.publication/, .venv/, SQLite, médias et rapports locaux sont ignorés. Les préfixes des cinq familles de rapports sont désormais explicitement ignorés s’ils sont générés à la racine. Aucun de ces chemins locaux n’est suivi selon git ls-files. Après commit des fichiers souhaités :

```bash
git archive --format=zip --output=/tmp/PharmaGest-rendu.zip HEAD
```

Cette commande inclut seulement les fichiers du commit HEAD. Ne pas l’assimiler à une sauvegarde de base/médias, ni attendre qu’elle contienne les modifications non commitées.

## Évolutions optionnelles : plans proposés, aucune implémentation autorisée

### Tendances des indicateurs

1. Fichiers prévus : pharmacy/views.py, dashboard.html, tests de période et guide dashboard.
2. Définir la période précédente de même longueur et les bornes inclusives.
3. Réutiliser les règles actuelles de ventes validées et réceptions effectives.
4. Calculer les agrégats de comparaison uniquement pour les données autorisées.
5. Afficher une variation absolue et un pourcentage lorsqu’il est défini.
6. Traiter explicitement le cas précédent égal à zéro.
7. Préserver les alertes actuelles indépendantes de la période analysée.
8. Risques : coût des requêtes et comparaison trompeuse sur périodes incomplètes.
9. Tests : bornes, zéro, remboursements, permissions et rendu des cinq rôles.
10. Commencer seulement après autorisation explicite des changements de vue.

### Tri global des stocks

1. Fichiers prévus : pharmacy/views.py, stock.html/includes filtres et tests de stock.
2. Définir les clés de tri serveur admises avec une liste fermée.
3. Appliquer le tri au QuerySet avant pagination.
4. Garder un second critère stable pour les ex aequo.
5. Préserver recherche, statut et tri dans l’URL de pagination.
6. Retirer la page courante quand le tri change.
7. Afficher le critère et le sens, avec repli natif sans JS.
8. Risques : confusion lot/médicament et tri local limité à une page.
9. Tests : plusieurs pages, ex aequo, paramètres invalides et permissions.
10. Commencer seulement après autorisation explicite des changements de vue.

### Filtres rupture et stock faible

1. Fichiers prévus : pharmacy/views.py, stock/catalogue, includes filtres et tests.
2. Définir le niveau médicament, distinct d’un lot épuisé.
3. Reprendre exactement l’exclusion des lots bloqués et périmés pour la disponibilité.
4. Comparer le stock disponible au seuil existant du médicament.
5. Conserver les médicaments sans lot dans la détection des ruptures.
6. Combiner filtres/recherche dans une requête serveur paginée.
7. Expliquer les quantités et l’état actif dans les libellés/chips.
8. Risques : agrégats incorrects et divergences avec la délivrance FEFO.
9. Tests : zéro lot, lots exclus, seuil atteint, cumul et pagination.
10. Commencer seulement après autorisation explicite des changements de vue.

### Actions en masse avec prévisualisation

1. Définir d’abord une action et un périmètre métier précis avec l’utilisateur.
2. Fichiers possibles : vues/formulaires/services existants, liste et template de prévisualisation.
3. Sélection explicite de références sans étendre silencieusement à toutes les pages.
4. Revalider chaque référence et permission côté serveur.
5. Prévisualiser objets concernés, conséquences et refus avant toute mutation.
6. Exiger une confirmation POST protégée par CSRF.
7. Utiliser les services métier et tracer l’opérateur pour chaque effet autorisé.
8. Risques : mutations nombreuses, états devenus obsolètes et atomicité ambiguë.
9. Tests : refus partiel, concurrence, limites de volume, rollback/idempotence et audit.
10. Ne pas commencer sans autorisation explicite de l’action et de son comportement transactionnel.

## Contrôles de clôture exécutés le 4 novembre

- `.venv/bin/python manage.py test --verbosity 1` : 90 tests découverts, **87 exécutés/réussis et 3 ignorés**, 158,595 s, OK (skipped=3). ReportLab absent de .venv ; les trois tests PDF textuels ne sont donc pas exécutés sur ce passage. La preuve des 90 succès avec ReportLab du 3 novembre reste distincte. Journal `/tmp/pharmagest-final-frontend-tests.log`.
- `manage.py check` : aucune anomalie ; `makemigrations --check --dry-run` : aucun changement.
- **34 tests JavaScript réussis** : cashier_math 12, operation_math 9, thème 5, contrastes 5, soumission 3.
- **3 tests Python d’outillage réussis**, 0,241 s.
- `git diff --check` : sans erreur ; fichiers métier protégés sans diff dans ce lot.
- Chemins locaux et rapports contrôlés avec git check-ignore et git ls-files : ignorés et non suivis.

Ces résultats consolident le checkpoint frontend. Ils ne transforment pas les contrôles manuels non renseignés en réussites. Aucun commit/merge/push effectué.
