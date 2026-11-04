# Jeu de démonstration local

Préparé le 4 novembre 2026 à la demande de l’utilisateur. Données fictives, prix illustratifs en ariary ; aucune référence médicale ou tarifaire officielle. Base SQLite habituelle, sans changement de schéma ou de logique applicative.

## Volume et parcours

30 médicaments dans 11 catégories, 6 fournisseurs dont un inactif, 12 clients fictifs, 32 lots, 12 commandes, 14 réceptions, 38 ventes dont deux brouillons, 36 paiements, trois retours. Les transactions utilisent les services existants. Historique de ventes réparti sur trois semaines ; approvisionnement initial antérieur. Un lot périmé provient du seed initial, distinct des réceptions récentes.

- Caisse : rechercher Paracétamol, observer les deux péremptions et le choix FEFO ; encaisser puis consulter le reçu.
- Ordonnance : chercher Amoxicilline, contrôler l’ordonnance avant validation.
- Stocks : comparer rupture, stock faible, lot proche, périmé et bloqué ; effectuer un inventaire fictif.
- Achats : commandes brouillon, commandée, partielle, reçue et annulée ; terminer une réception partielle.
- Retours : consulter les trois exemples (avec et sans remise en stock), puis tester sur une vente encore retournable.
- Gestion : périodes, rapports, paiements espèces/mobile/carte, mouvements et audit. Les références électroniques et remboursements sont simulés, aucune transaction financière réelle.
- Catalogue : une fiche inactive et une non autorisée permettent de vérifier les exclusions.

Les codes commençant par DEMO sont des identifiants fictifs de recherche, pas des codes EAN homologués.

## Comptes

| Identifiant | Groupe | Démonstration principale |
|---|---|---|
| demo_direction | Administrateur | Ensemble des modules et utilisateurs, sans statut superutilisateur |
| demo_pharmacien | Pharmacien responsable | Délivrance, ordonnance, retours, vérification manuelle des paiements |
| demo_caisse | Caissier | Vente et encaissement espèces ; pas d’autorisation de retour ou vérification électronique |
| demo_stock | Gestionnaire de stock | Catalogue, fournisseurs, commandes, réception et inventaire |
| demo_gestion | Responsable de gestion | Consultation, rapports, audit ; pas de transaction commerciale |

Les cinq mots de passe distincts sont uniquement dans `.publication/ACCES_DEMONSTRATION.txt`, fichier privé local (0600) ignoré par Git. Ne pas le publier ou le joindre aux rapports. Le compte `demo_admin` existant et son mot de passe sont préservés ; son ancien mot de passe ne peut pas être extrait du hash.

Connexion sur le serveur habituel : `http://127.0.0.1:8000/comptes/login/`. Ces comptes ne concernent pas les bases temporaires des lanceurs de recette. Une déconnexion est nécessaire pour changer de rôle.

## Sauvegarde et limites

Sauvegarde SQLite avant remplacement : `backups/avant-demo-20261104-112651.sqlite3`, permissions 0600. Aucun média supprimé. Copie SQLite de la base préparée dans la base habituelle après contrôles ; aucune suppression de fichier ou migration destructive. Ne pas restaurer pendant qu’un serveur écrit dans la base.

Le jeu évolue pendant les démonstrations : un passage ultérieur peut afficher des stocks et compteurs différents. Ne pas relancer `seed_demo` pour le réinitialiser : cette commande ignore une base déjà initialisée. Les scripts ponctuels de préparation ne constituent pas une nouvelle commande de remise à zéro maintenue.
