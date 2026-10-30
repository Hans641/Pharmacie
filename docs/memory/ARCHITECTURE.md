# Architecture technique

Vérifiée le 30 octobre 2026 à partir du code, de la migration initiale et du dossier de conception. Décrire ici les structures, conserver l’avancement dans `DEVELOPMENT_STATUS.md`.

## Organisation

| Emplacement | Responsabilité |
|---|---|
| `config/settings.py`, `urls.py`, `wsgi.py` | Configuration environnement, routes, serveur WSGI |
| `pharmacy/models.py` | 15 modèles métier et contraintes |
| `pharmacy/forms.py` | ModelForms et formulaires des opérations |
| `pharmacy/services.py` | Permissions et transactions commerciales/stock, audit |
| `pharmacy/views.py` | Vues fonctionnelles, accès, requêtes, création de fiches, orchestration et rapports |
| `pharmacy/templatetags/ui.py` | Formatage, widgets accessibles, groupes de champs et données de présentation |
| `templates/`, `templates/includes/` | Pages Django et composants partagés ; authentification dans `registration/` |
| `static/css/`, `static/js/` | Bootstrap local, tokens et composants, interactions progressives |
| `pharmacy/pdf.py` | ReportLab si disponible, PDF texte de secours sinon |
| `pharmacy/management/commands/` | Rôles, données fictives, sauvegarde et restauration |
| `pharmacy/tests.py`, `test_ui.py`, `tools/` | Tests métier, présentation et calculs JS ; outil navigateur optionnel |

Python observé : 3.12.3 ; Django 6.0.4. Dépendances déclarées dans `requirements.txt` : Django 6.0.4, Pillow 12.1.0, ReportLab >=4.4,<5. Aucun React, Eloquent ou build front requis.

## Base et relations

SQLite configuré dans `settings.py`, chemin surchargeable par `DATABASE_PATH`, délai 20 s et transactions `IMMEDIATE`. La migration métier livrée est `pharmacy/migrations/0001_initial.py`, dépendante du modèle utilisateur Django. Les tables auth, sessions et permissions viennent de Django. Le schéma attendu est analysé ; aucun contenu métier de la base active n’a été inventorié pour cette mémoire.

| Modèle | Relations / rôle |
|---|---|
| Category | Une catégorie possède plusieurs Medicine |
| Medicine | FK Category ; plusieurs Lot et PurchaseLine ; code-barres unique nullable |
| Supplier | Plusieurs Purchase |
| Customer | Plusieurs Sale ; client facultatif sur la vente |
| Purchase | FK Supplier et auteur ; plusieurs PurchaseLine et Receipt |
| PurchaseLine | FK Purchase et Medicine ; quantité commandée/reçue, prix historique |
| Lot | FK Medicine ; numéro, péremption, quantité, coût, blocage |
| Receipt | FK Purchase et auteur ; UUID unique ; plusieurs ReceiptLine |
| ReceiptLine | FK Receipt, PurchaseLine et Lot ; quantité et coût reçus |
| Sale | FK Customer facultative et auteur ; lignes, retours et paiement |
| SaleLine | FK Sale et Lot ; quantités vendues/retournées, prix et coût historiques |
| Payment | OneToOne Sale ; méthode, montant, confirmation et vérificateur |
| SaleReturn | FK Sale, SaleLine et auteur ; quantité, montant, motif, référence et UUID unique |
| StockMovement | FK Lot et auteur ; variation signée ; liens facultatifs réception/vente/retour |
| AuditLog | FK auteur ; action, cible descriptive et horodatage |

Les FK métier sont protégées par `PROTECT`. Contraintes SQL : prix positifs, quantités de transaction positives, stock non négatif, reçu/retourné limité à la quantité d’origine, unicité `(medicine, number)` des lots. Montants stockés en `DecimalField` à deux décimales. Voir `../CONCEPTION.md` pour le MLD complet.

## Fonctionnement transactionnel

- Achat : `draft → ordered → partial → received` ; annulation seulement avant réception. Une commande seule ne touche pas le stock.
- Réception : transaction, jeton unique, contrôle du reliquat et de la cohérence du lot, incrément du stock, mouvement et audit.
- Panier : FEFO par péremption puis identifiant, ou lot explicite ; retranche les lignes du même panier pour l’ajout. Un brouillon ne réserve pas globalement le stock.
- Vente : `draft → validated`, recontrôle des lots et ordonnances, décrément SQL conditionnel, paiement unique, mouvements et audit dans la même transaction. Revalidation sans seconde sortie.
- Retour : quantité encore retournable contrôlée, remboursement référencé, prix historique, UUID unique ; remise en stock refusée si lot bloqué ou périmé.
- Inventaire : comptage physique et état bloqué, mouvement de l’écart, motif et audit.

`select_for_update()` ne fournit pas de verrou de ligne effectif sur SQLite : la protection repose aussi sur la transaction IMMEDIATE et les mises à jour conditionnelles. Un verrou temporaire peut produire un refus à réessayer.

## Routes et sécurité

`config/urls.py` relie `/` au tableau de bord ; `/catalogue/<key>/` aux vues génériques de fiches ; `/achats/`, `/ventes/`, `/stocks/` aux opérations ; `/mouvements/`, `/audit/`, `/utilisateurs/`, `/rapports/` aux consultations correspondantes. `/documents/<kind>/<pk>.pdf` exporte les documents. `/comptes/` utilise Django auth, `/admin/` l’administration.

Authentification par session, permissions Django et CSRF. Les photos `/media/` sont servies avec authentification et permission `view_medicine` ; ne pas exposer directement MEDIA_ROOT. L’admin interdit les écritures sur les opérations commerciales ; ce n’est pas un audit inviolable contre un administrateur de base.

## Front et configuration

`app.js` : navigation, confirmations, recherche progressive et soumission protégée ; `forms.js` : aide à la saisie et assistant médicament ; `operations.js` et `operation-math.mjs` : prévisualisation des opérations ; `cashier.js` et `cashier-math.mjs` : caisse et calcul exact en centimes BigInt. Les mutations restent des POST Django avec repli sans JS.

Les variables sont lues par `os.environ` ; `.env` n’est pas chargé automatiquement. SMTP utilise la console par défaut. ReportLab est absent de l’environnement observé : le moteur PDF texte est utilisé. Le schéma PostgreSQL n’a pas été validé.

## Multi-tenant

**Absent.** Une configuration de pharmacie et une base commune, sans modèle Tenant/Organisation, identifiant de tenant ni middleware d’isolation. Les permissions sont globales à l’installation. Ne pas déployer cette architecture comme SaaS multi-tenant sans conception explicite et tests d’isolation.

### Thèmes partagés (30 octobre 2026)

`base.html` charge le petit script local `theme.js` en tête, puis `themes.css` après les styles de composants. Les palettes utilisent les tokens communs ; seul `pharmagest-theme` est mémorisé côté navigateur. Sans JS, `prefers-color-scheme` détermine la palette. Un sélecteur natif partagé en pied de page permet la préférence manuelle. Les variables sombres sont restreintes à l'écran, l'impression et les PDF restant indépendants.
