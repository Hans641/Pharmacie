# Couverture du cahier des charges

| Module / règles | Réalisation |
|---|---|
| A — Authentification | Django auth, comptes, rôles cumulables, permissions serveur, réinitialisation par e-mail, désactivation |
| B — Médicaments | Champs demandés, photos contrôlées, recherche, filtre catégorie/état, tri, pagination, archivage |
| C — Catégories | Création, consultation, modification, recherche et suppression protégée |
| D — Fournisseurs | Fiche complète, recherche nom/téléphone, historique et montants des commandes, désactivation ; réceptions dans les commandes |
| E — Clients | Coordonnées minimales, état, historique et comptoir anonyme |
| F — Achats | Brouillons multilignes, validation, annulation avant réception, réceptions partielles, prix historiques et bons PDF |
| G — Stocks | Lots, FEFO, validité/blocage, mouvements, comptage physique, alertes |
| H — Caisse | Panier multilignes, choix des lots, paiements intégraux, validation atomique idempotente, prix conservés, reçu |
| I — Retours | Vente et lot d’origine, plafond de quantité, motif, auteur, référence du remboursement et remise en stock contrôlée |
| J — Tableau de bord | Données réelles, périodes, ventes, achats reçus, classement des produits, stocks faibles, péremptions, séparation CA / encaissements / marge |
| K — PDF | Reçu, facture, commande, réception, stocks, ventes, achats, péremptions ; ReportLab si installé, moteur PDF texte de secours hors ligne |
| RG01–RG03 | Identifiants automatiques, unicité code-barres et validation formulaires/services/contraintes SQL |
| RG04–RG06 | Commande sans mouvement, réceptions à jeton unique et ventes à statut validé |
| RG07–RG08 | Mises à jour conditionnelles du stock, contrôles lots valides et non bloqués |
| RG09–RG10 | Auteurs, dates, audit, opérations commerciales en lecture seule dans l’admin, retours compensatoires |
| RG11–RG12 | Permissions sur les vues/services, copie des prix et coûts dans les lignes historiques |
| Tests demandés | Modèles, formulaires, images, stock, paiements, retours, PDF, accès, sauvegarde/restauration et validations concurrentes |
| Livrables | Sources, migrations, SQLite locale de démonstration, pages, formulaires, modules métier, rôles, rapports, données fictives, tests et documentation |

## Points à configurer avant exploitation

Les mentions fiscales et les procédures professionnelles dépendent du territoire : les documents livrés portent une mention de démonstration configurable. Une validation locale est nécessaire avant utilisation réelle. PostgreSQL est une évolution documentée ; la configuration livrée est SQLite. Les e-mails sont affichés dans la console tant que SMTP n’est pas configuré. La protection contre les tentatives répétées de connexion doit être ajoutée au déploiement public.

Le logiciel enregistre la confirmation manuelle de paiements électroniques après vérification externe ; aucune intégration à un prestataire n’est fournie. Les remboursements sont enregistrés après exécution externe. Les retours compensatoires réalisent les annulations de ventes validées sans suppression de l’historique.
