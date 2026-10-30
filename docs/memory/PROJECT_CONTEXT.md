# Contexte du projet

État vérifié le 30 octobre 2026. Point d’entrée de reprise : `../../AGENTS.md`, puis `DEVELOPMENT_STATUS.md`.

## Identité et objectif

**PharmaGest** centralise la gestion administrative et commerciale d’une pharmacie à Madagascar : approvisionnements, médicaments, lots, délivrance, encaissements et traçabilité. Source : `Cahier des charges projet pharmacie.pdf`, relu pour cette mémoire ; correspondance détaillée dans `../CONFORMITE.md`.

La demande de mémoire mentionne « Laravel Rizicole SaaS » et Eloquent. Ces éléments ne correspondent ni au dépôt ni au cahier des charges. Aucun domaine rizicole, abonnement SaaS ou mécanisme multi-tenant n’est établi. Cette mémoire décrit exclusivement le projet Django présent.

## Utilisateurs

Cinq groupes cumulables définis par `pharmacy/management/commands/setup_roles.py` : Administrateur, Pharmacien responsable, Gestionnaire de stock, Caissier, Responsable de gestion. Les permissions effectives font foi ; le nom du rôle seul ne suffit pas. Le caissier standard ne vérifie pas les paiements électroniques et n’autorise pas les retours.

Le contexte UX fourni par l’utilisateur est celui de professionnels pressés au comptoir, debout, parfois sur tablette/téléphone et avec une connexion instable. L’objectif de vente en moins de 30 secondes reste à mesurer.

## Périmètre métier

- Authentification, comptes actifs/inactifs, rôles et audit.
- Catalogue : catégories, médicaments, photos, autorisation de délivrance et ordonnance requise.
- Fournisseurs et clients ; vente comptoir sans client identifié.
- Commandes distinctes des réceptions, livraisons partielles, lots et coûts historiques.
- Stock physique, disponibilité, FEFO, blocage, inventaires et mouvements.
- Vente en brouillon, panier, validation et encaissement intégral atomiques.
- Retours partiels compensatoires, référence du remboursement et remise en stock contrôlée.
- Tableau de bord, alertes, documents et rapports PDF, sauvegarde/restauration SQLite.

## Contraintes

Django, SQLite livré, templates HTML, Bootstrap et ressources locales ; français, ariary, fuseau Madagascar. Préserver règles métier et permissions pendant la refonte UI. Accessibilité et responsive sont des cibles à vérifier, pas une certification obtenue.

Le projet est pédagogique. Il n’automatise ni diagnostic ni prescription, ni comptabilité générale, ni passerelle bancaire. La délivrance et les remboursements nécessitent des contrôles professionnels. Mise en production : voir `../EXPLOITATION.md` ; conformité réglementaire locale non établie.

## Guides de référence

`../../README.md` : installation et fonctions ; `../UTILISATION.md` : parcours ; `../CONCEPTION.md` : MCD/MLD et séquences ; `../EXPLOITATION.md` : déploiement et sauvegardes ; `../REFONTE_UI.md`, `../CONCEPTION_EXPERIENCE.md`, `../PARCOURS_OPERATIONS.md`, `../RECETTE_CAISSE.md` : détails des itérations UI.
