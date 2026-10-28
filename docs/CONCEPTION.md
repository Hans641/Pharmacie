# Dossier de conception

## Architecture

Django MVT : `pharmacy/models.py` définit les relations et contraintes SQL ; `forms.py` valide les saisies ; `services.py` centralise les mutations atomiques et leurs permissions ; `views.py` applique les contrôles d’accès et présente les données. Les modèles métier sont regroupés dans une application pour garder le projet lisible ; les modules sont séparés par responsabilités. L’administration laisse les opérations commerciales en lecture seule pour éviter les modifications directes du stock.

`config/` contient configuration, routage et WSGI. `templates/pharmacy/` regroupe les écrans métier, `templates/registration/` l’authentification, `static/css/` le style. Les commandes sont dans `pharmacy/management/commands/` et les tests dans `pharmacy/tests.py`.

## MCD (Mermaid)

```mermaid
erDiagram
    CATEGORY ||--o{ MEDICINE : classe
    MEDICINE ||--o{ LOT : possede
    SUPPLIER ||--o{ PURCHASE : fournit
    PURCHASE ||--o{ PURCHASE_LINE : contient
    MEDICINE ||--o{ PURCHASE_LINE : commande
    PURCHASE ||--o{ RECEIPT : receptionne
    RECEIPT ||--|{ RECEIPT_LINE : contient
    PURCHASE_LINE ||--o{ RECEIPT_LINE : livre
    LOT ||--o{ RECEIPT_LINE : alimente
    CUSTOMER o|--o{ SALE : achete
    SALE ||--o{ SALE_LINE : contient
    LOT ||--o{ SALE_LINE : delivre
    SALE ||--o| PAYMENT : encaisse
    SALE ||--o{ SALE_RETURN : compense
    SALE_LINE ||--o{ SALE_RETURN : retourne
    LOT ||--o{ STOCK_MOVEMENT : retrace
    USER ||--o{ STOCK_MOVEMENT : realise
    USER ||--o{ AUDIT_LOG : signe
    USER ||--o{ PURCHASE : cree
    USER ||--o{ SALE : ouvre
    USER ||--o{ RECEIPT : recoit
    USER ||--o{ SALE_RETURN : autorise
    USER ||--o{ PAYMENT : verifie
```

## MLD

Les clés `id` sont des entiers auto-incrémentés. Les références ci-dessous sont des clés étrangères protégées (`PROTECT`), sauf les relations des groupes Django. Les migrations font foi pour les types et contraintes exacts.

| Table | Attributs principaux et relations |
|---|---|
| Category | id, name UNIQUE, description |
| Medicine | id, category_id FK, name, generic_name, form, dosage, manufacturer, barcode UNIQUE NULL, photo, purchase_price, sale_price, threshold, active, authorized, requires_prescription, created_at |
| Supplier | id, name, address, phone, email, tax_id, contact, active |
| Customer | id, name, phone, address, active |
| Purchase | id, supplier_id FK, author_id FK User, status, created_at |
| PurchaseLine | id, purchase_id FK, medicine_id FK, quantity, received, unit_price |
| Receipt | id, purchase_id FK, author_id FK, token UUID UNIQUE, created_at |
| ReceiptLine | id, receipt_id FK, purchase_line_id FK, lot_id FK, quantity, unit_cost |
| Lot | id, medicine_id FK, number, expires_on, quantity, received_quantity, unit_cost, blocked ; UNIQUE(medicine_id, number) |
| Sale | id, customer_id FK NULL, author_id FK, status, created_at, validated_at NULL, prescription_checked |
| SaleLine | id, sale_id FK, lot_id FK, quantity, returned, unit_price, unit_cost |
| Payment | id, sale_id FK UNIQUE, method, amount, confirmed, reference, verified_by_id FK, created_at |
| SaleReturn | id, sale_id FK, line_id FK, quantity, reason, restock, amount, refund_reference, token UUID UNIQUE, author_id FK, created_at |
| StockMovement | id, lot_id FK, quantity signée, kind, reason, receipt_id FK NULL, sale_id FK NULL, return_record_id FK NULL, author_id FK, created_at |
| AuditLog | id, author_id FK, action, target, created_at |
| Utilisateurs | Tables natives auth_user, auth_group, auth_permission et tables associatives |

Les prix utilisent des décimaux à deux chiffres après la virgule. Les coûts historiques sont enregistrés par lot et ligne de vente. Les quantités ne peuvent pas être négatives ; les quantités de transaction et les prix doivent être strictement positifs. Les quantités reçues et retournées sont limitées aux quantités d’origine.

Le stock physique est matérialisé dans `Lot.quantity` pour les mises à jour atomiques et sa variation est toujours associée à un mouvement. Le stock disponible exclut les lots périmés et bloqués. Les médicaments inactifs ou non autorisés sont également refusés par le service de vente.

## Cas d’utilisation

```mermaid
flowchart LR
    A[Administrateur] --> U[Gérer les comptes et attribuer les rôles]
    P[Pharmacien responsable] --> M[Autoriser les médicaments et contrôler les lots]
    G[Gestionnaire de stock] --> C[Commander et réceptionner]
    G --> I[Inventorier et bloquer des lots]
    K[Caissier] --> V[Préparer et encaisser une vente]
    P --> R[Contrôler un retour et tracer le remboursement]
    D[Responsable de gestion] --> T[Consulter les indicateurs et exporter les rapports]
```

## Validation d’une vente

```mermaid
sequenceDiagram
    actor Caissier
    participant Vue
    participant Service
    participant BD
    Caissier->>Vue: Confirmer le paiement et la délivrance
    Vue->>Vue: Authentification, permission, formulaire et CSRF
    Vue->>Service: validate_sale(vente, paiement)
    Service->>BD: BEGIN IMMEDIATE (SQLite)
    Service->>BD: Charger la vente et vérifier le statut
    alt Vente déjà validée
        Service-->>Vue: Même vente, aucun nouveau mouvement
    else Vente en brouillon
        Service->>Service: Vérifier paiement, ordonnance et autorisations
        loop Chaque ligne
            Service->>BD: UPDATE lot SET quantity=quantity-q WHERE quantity>=q et lot valide
            Service->>BD: Insérer mouvement de sortie
        end
        Service->>BD: Enregistrer paiement, statut validé et audit
        Service->>BD: COMMIT
        Service-->>Vue: Vente validée
    end
    Vue-->>Caissier: Confirmation et reçu PDF
```

Toute erreur provoque un rollback de l’ensemble, y compris si une première ligne était disponible et qu’une ligne suivante ne l’est plus. Les saisies ne peuvent pas modifier directement les prix historiques d’une vente validée.

## Cycle des commandes

```mermaid
stateDiagram-v2
    [*] --> Brouillon
    Brouillon --> Commandee: validation d’une commande non vide
    Brouillon --> Annulee
    Commandee --> Annulee: aucune réception
    Commandee --> Partielle: réception d’une partie
    Commandee --> Receptionnee: réception complète
    Partielle --> Partielle: livraison complémentaire
    Partielle --> Receptionnee: réception du reliquat
```

Une réception porte un jeton unique et des lignes distinctes de la commande. La même réception ne peut donc alimenter deux fois le stock. Le service accepte plusieurs lignes atomiques ; l’écran propose de réceptionner les lots successivement.
