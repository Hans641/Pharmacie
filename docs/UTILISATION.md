# Guide d’utilisation

## Première connexion et utilisateurs

Se connecter avec le compte créé par `createsuperuser`, ou avec le compte `demo_admin` et le mot de passe affiché par `seed_demo`. Le menu présente les fonctions autorisées. Le lien des paramètres dans l’en-tête permet de changer son mot de passe. « Quitter » ferme la session.

Dans **Utilisateurs & rôles**, l’administrateur crée les comptes, renseigne leur e-mail et attribue un ou plusieurs rôles. Décocher « Actif » désactive un compte. La réinitialisation par e-mail nécessite un serveur SMTP en exploitation ; en développement, l’e-mail et son lien s’affichent dans la console du serveur.

| Rôle | Accès principal |
|---|---|
| Administrateur | Tous les modules métier, gestion des comptes et rôles existants |
| Pharmacien responsable | Catalogue, contrôle des lots, achats, caisse, retours et vérification des paiements |
| Gestionnaire de stock | Catalogue, fournisseurs, commandes, réceptions, inventaires |
| Caissier | Consultation des produits/lots, clients, caisse et encaissement espèces |
| Responsable de gestion | Consultation du catalogue, achats, ventes, stocks, rapports et audit |

Les permissions détaillées et les droits individuels sont ajustables dans l’administration Django par un superadministrateur. Les comptes créés par l’interface métier n’ont pas automatiquement accès à `/admin/`.

## Catalogue

Créer d’abord une catégorie, puis un médicament. Les prix doivent être strictement positifs ; le code-barres est unique s’il est renseigné. Une photo réelle JPEG, PNG ou WebP de 5 Mo au maximum peut être ajoutée. L’autorisation de délivrance doit être accordée explicitement. Cocher « Ordonnance requise » lorsque nécessaire.

La liste propose recherche par nom/générique/code-barres, catégorie, état, tri et pagination. Cliquer sur le nom ouvre la fiche. « Archiver » retire le produit des nouvelles ventes sans effacer ses opérations. Une catégorie utilisée ne peut pas être supprimée.

Créer les fournisseurs et, si nécessaire, les clients. Un client est facultatif pour une vente comptoir. Les coordonnées se limitent aux besoins commerciaux.

## Approvisionnement

1. Dans **Achats & réceptions**, créer une commande et choisir un fournisseur actif.
2. Ajouter autant de lignes que nécessaire avec médicaments, quantités et prix.
3. Confirmer la commande. Aucun stock n’est ajouté à ce stade.
4. Choisir **Réceptionner** et renseigner la ligne, la quantité effectivement reçue, le numéro de lot et la péremption.
5. Répéter pour les autres lots/lignes ou livraisons. La commande devient partiellement puis entièrement réceptionnée.
6. Télécharger le bon de commande ou les bons de réception.

Un lot déjà connu ne peut être réutilisé qu’avec le même médicament, la même péremption et le même coût. Les marchandises déjà périmées sont refusées à la réception. Une commande peut être annulée uniquement avant toute réception.

## Caisse

1. Ouvrir une nouvelle vente, avec un client ou en comptoir.
2. Choisir le médicament et la quantité. Laisser le lot vide pour utiliser FEFO ; les quantités peuvent se répartir sur plusieurs lots.
3. Contrôler les lots réellement délivrés. Un lot particulier peut être choisi explicitement. Retirer une ligne si nécessaire.
4. Choisir le mode de paiement, contrôler l’ordonnance si elle est nécessaire et confirmer l’encaissement.
5. Pour mobile money/carte/virement, un utilisateur habilité vérifie le statut directement auprès du prestataire et saisit la référence avant confirmation.
6. Valider puis télécharger le reçu ou la facture.

Le panier ne réserve pas le stock. La disponibilité et la péremption sont revérifiées au moment de la validation : une autre vente peut rendre un panier indisponible. Les prix des lignes sont conservés. Un double clic ou une nouvelle validation d’une vente déjà encaissée ne redéduit pas le stock.

## Retours et inventaires

Sur une vente validée, un responsable habilité ouvre **Enregistrer un retour**, sélectionne la ligne et la quantité, saisit un motif et la référence du remboursement effectivement réalisé. La remise en stock n’est cochée qu’après contrôle de l’éligibilité du produit. Les lots périmés ou bloqués ne sont pas réintégrés par ce mécanisme. Pour annuler totalement une vente, traiter toutes ses lignes par des retours compensatoires.

Dans **Stocks & lots**, **Inventaire / blocage** permet de saisir le comptage physique et un motif. La différence est enregistrée dans les mouvements, avec l’auteur. Cocher « Bloquer » interdit la vente du lot. Un stock physique peut inclure des unités périmées ou bloquées ; le stock disponible du catalogue les exclut.

## Suivi

Le tableau de bord présente les indicateurs accessibles au rôle, avec une période sélectionnable. Le CA est brut ; les remboursements et les encaissements nets sont présentés séparément. La marge n’inclut pas les autres charges. Les classements de produits indiquent les quantités vendues brutes.

Les rapports de stock et de péremption donnent la situation actuelle ; les périodes s’appliquent aux ventes et aux réceptions d’achat. Les retours cumulés des ventes du rapport peuvent inclure des remboursements postérieurs à la période ; le montant remboursé pendant la période est également indiqué.
