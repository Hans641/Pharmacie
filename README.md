# PharmaGest

Application Django de gestion de pharmacie, créée à partir de **Cahier des charges projet pharmacie.pdf**. Interface en français, montants en ariary, fuseau Madagascar. Python 3.12+, Django 6.0, SQLite, Bootstrap 5 et CSS adapté aux mobiles.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_roles
python manage.py createsuperuser
python manage.py runserver
```

Ouvrir http://127.0.0.1:8000/ et se connecter. `.env.example` décrit les variables disponibles : le fichier `.env` n’est pas chargé automatiquement. Exporter les valeurs dans le shell ou les configurer dans le gestionnaire de service.

Pour une démonstration sur une base vide :

```bash
python manage.py seed_demo
```

La commande affiche un mot de passe aléatoire pour `demo_admin`. Il est possible de fournir `DEMO_PASSWORD` via l’environnement. Elle est idempotente et ne remplace jamais un compte existant. Les médicaments, fournisseurs et transactions sont **fictifs**.

Dans l’environnement de création, Django et Pillow ont été installés depuis le cache local. ReportLab n’était pas accessible sans réseau : les PDF utilisent alors un moteur texte de secours, multi-page. Une installation complète de `requirements.txt` active automatiquement ReportLab. Bootstrap 5.3.8, les icônes SVG, le CSS métier et le JavaScript sont servis localement. Aucune police ni ressource distante n’est nécessaire à l’interface.

## Fonctions disponibles

- Connexion, déconnexion POST, changement et réinitialisation du mot de passe par lien à usage limité ; comptes actifs/inactifs et cinq rôles cumulables.
- Médicaments avec photos validées (JPEG, PNG, WebP, 5 Mo max), catégories, recherche, filtre, tri, pagination et archivage.
- Fournisseurs et clients, fiches détaillées et historique accessible selon les permissions.
- Commandes en brouillon, lignes multiples, validation, annulation avant réception, réceptions partielles par lot et bons PDF.
- Stock physique par lot, péremption, blocage, inventaire et mouvements horodatés avec auteur.
- Caisse en brouillon, choix FEFO automatique ou lot explicite, prix historiques, encaissement atomique et reçu/facture PDF.
- Contrôle des médicaments autorisés et des ordonnances requises. Les lots bloqués ou périmés sont exclus des ventes.
- Espèces ; paiements électroniques uniquement après vérification manuelle auprès du prestataire par un utilisateur habilité, avec référence. Aucun paiement électronique automatique n’est simulé.
- Retours partiels avec motif, remboursement déjà effectué et sa référence, réintégration optionnelle après contrôle, sans effacement de la vente.
- Tableau de bord calculé, périodes, CA brut, encaissements nets, remboursements, marge commerciale, achats réceptionnés, meilleurs produits et alertes.
- Rapports PDF des stocks, péremptions, ventes et achats ; journal d’audit ; sauvegarde et restauration SQLite vérifiées.

Les paiements partiels, passerelles de paiement, comptabilité générale et prescriptions automatiques ne sont pas implémentés. Les ventes sont intégralement encaissées à la validation. Une annulation après validation se fait par des retours compensatoires sur toutes les lignes ; chaque remboursement est référencé.

## Vérification

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

La suite couvre les calculs, permissions, images, formulaires, commandes/réceptions, FEFO, atomicité, doubles validations, paiements, retours, PDF, sauvegarde et restauration, ainsi que des validations concurrentes. Les tests de concurrence utilisent deux connexions et acceptent un refus temporaire de verrouillage SQLite ; ils vérifient l’absence de sortie double et de stock négatif.

## Documentation

- [Guide d’utilisation](docs/UTILISATION.md)
- [Conception, MCD, MLD et séquences](docs/CONCEPTION.md)
- [Exploitation, sauvegardes et déploiement](docs/EXPLOITATION.md)
- [Couverture du cahier des charges](docs/CONFORMITE.md)

Le projet est une application pédagogique. Avant exploitation réelle, faire valider les mentions des documents et les procédures de délivrance, de remboursement, de conservation et de protection des données par les responsables compétents.

## Interface et recette UX

La refonte comprend une caisse au clavier (F2/F4), une aide au calcul de monnaie, une navigation mobile, des listes en cartes sur téléphone et des composants accessibles. Les contrôles serveur restent inchangés.

- [Audit UX initial](docs/AUDIT_UX.md)
- [Design system et modifications fichier par fichier](docs/REFONTE_UI.md)
- [Checklist et recette par rôle](docs/RECETTE_UX.md)

Le script optionnel `tools/ux_browser_check.cjs` contrôle les quatre largeurs cibles sur un serveur lancé localement. Voir la recette pour les conditions et les limites de validation.

### Formulaires accompagnés

La création et la modification d’un médicament proposent trois étapes avec récapitulatif. Les retours inline aident à corriger les saisies simples ; Django conserve les validations métier. Sans JavaScript, toutes les sections restent visibles. Les notifications de succès sont fermables manuellement et les recherches conservent les résultats pendant le chargement.

Voir [la conception et la recette de cette itération](docs/CONCEPTION_EXPERIENCE.md). Le contrôle navigateur facultatif s’active avec `UX_WIZARD=1`.

### Réception, inventaire et retour

Ces opérations disposent d’un récapitulatif avant confirmation : reliquat et valeur reçue, écart d’inventaire signé, montant du retour et effet de la remise en stock. Les estimations sont recalculées à l’enregistrement côté serveur.

Voir [les parcours opérationnels et leur recette](docs/PARCOURS_OPERATIONS.md). Tests de calcul sans dépendance : `node tools/operation_math.test.mjs`.
