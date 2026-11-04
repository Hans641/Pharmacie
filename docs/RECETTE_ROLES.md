# Recette finale par rôle — 4 novembre 2026

## Preuves serveur réellement exécutées

Commande : `.venv/bin/python tools/run_role_journeys.py`. Base/médias temporaires, authentification de cinq comptes fictifs via la route login et POST avec contrôle CSRF actif. Aucun serveur réseau requis. Les mutations passent par les vues et services existants. Les mots de passe/CSRF/cookies ne sont pas enregistrés dans le rapport.

Rapport `/tmp/pharmagest-role-report-p9de2osq/summary.json` : **15/15 OK HTTP/état base**. Cinq parcours positifs, neuf refus GET/POST sans mutation et un rejet sans CSRF. L’avertissement « Forbidden (CSRF token missing.) » est attendu pour ce dernier cas, pas un défaut applicatif.

| Rôle | Parcours exécuté via Client Django | Résultat |
|---|---|---|
| Caissier | Création brouillon comptoir, ajout FEFO, refus ordonnance manquante sans paiement/stock déduit, validation avec ordonnance, reçu/nouvelle vente disponibles, retour absent | OK serveur |
| Pharmacien | Vente avec contrôle ordonnance, retour fictif référencé, remise d’une unité en stock, un seul paiement conservé et historique affiché | OK serveur |
| Stock | Réception d’une unité avec reliquat maintenu, lot créé, inventaire/blocage avec quantité identique, mouvement inventory enregistré | OK serveur |
| Gestion | Rapports, audit, mouvements et quatre routes PDF accessibles | OK serveur, PDF secours texte dans ce passage |
| Administrateur | Création compte fictif avec groupe Caissier, actif sans superuser, audit enregistré | OK serveur |

Accès refusés sans mutation vérifiés : caissier vers retour/inventaire/création utilisateur ; stock vers ventes/création utilisateur ; gestion vers création vente/inventaire/réception ; pharmacien vers création utilisateur. Des permissions cumulées supplémentaires peuvent autoriser davantage d’actions ; ce passage teste les cinq groupes standards séparés.

Premier rapport 4zyj8bfz : 14/15 OK, échec dans l’assertion du type de mouvement du stock (outil attendait block). Lecture de services.adjust_stock : l’inventaire/blocage trace inventory. Assertion d’outil corrigée, aucun changement applicatif ; second passage 15/15 OK.

Ce résultat n’exécute ni JavaScript, ni navigation clavier réelle, ni rendu visuel. Il ne remplace pas les anciennes matrices navigateur et ne certifie pas tous les parcours utilisateur. Les vérifications PDF ci-dessus portent sur type/signature/accessibilité serveur, pas sur ReportLab ; la recette ReportLab du lot précédent reste une preuve distincte.

## Passage humain dans un même serveur fictif

```bash
.venv/bin/python tools/run_manual_review.py --role all
```

Choisir un mot de passe temporaire différent des mots de passe réels. Utiliser exclusivement le port annoncé ; toutes les opérations de cette recette restent fictives. Les cinq comptes utilisent ce mot de passe temporaire, saisi sans écho. Garder le terminal ouvert. La base de cette recette est neuve : elle ne conserve pas les ventes du contrôle serveur précédent.

Se déconnecter entre chaque compte, puis se reconnecter via l’écran de connexion ; ne pas supposer qu’un lien de rôle change la session. Les liens propres à chaque rôle sont affichés dans le terminal. Commencer sur desktop à 100 %, puis refaire les points visuels critiques à 360 px et en sombre.

1. **ux_caissier** : ouvrir le brouillon affiché. Il contient un produit avec ordonnance. Tenter de confirmer l’encaissement sans contrôle d’ordonnance et lire l’erreur ; vérifier la conservation du panier. Simuler ensuite le contrôle avec une ordonnance fictive, payer en espèces, vérifier total/monnaie et message de réussite. Ouvrir le reçu, puis Nouvelle vente ; vérifier brouillon vide. Aucun retour ou paiement électronique vérifié ne doit être proposé au caissier standard.
2. **ux_pharmacien** : sur sa vente fictive, contrôler les informations de délivrance/lot/ordonnance, encaisser, puis ouvrir Enregistrer un retour. Retourner une unité avec raison et référence fictive de remboursement déjà effectué hors application ; ne pas utiliser de coordonnées financières réelles. Vérifier le récapitulatif, la confirmation, l’historique du retour et la quantité remise en stock. Le logiciel ne verse pas un remboursement.
3. **ux_stock** : ouvrir la commande partiellement reçue annoncée, relever commandé/reçu/restant. Recevoir une unité dans un lot au numéro fictif unique et une date future ; vérifier reliquat, nouveau lot et mouvement. Ouvrir l’inventaire de ce lot, conserver sa quantité, bloquer avec un motif ; vérifier l’état et la trace. Les actions de vente restent absentes.
4. **ux_gestion** : consulter les listes et rapports, appliquer une période, télécharger les quatre exports autorisés. Les boutons de modification/encaissement/inventaire doivent être absents. Vérifier les titres et la conservation de la période où elle s’applique.
5. **ux_administrateur** : créer un compte entièrement fictif actif avec rôle Caissier, ouvrir sa fiche et retrouver la trace dans Audit. Vérifier les messages et les libellés de rôles, sans modifier les comptes des autres parcours.

Pour chaque parcours : messages compréhensibles, saisies conservées après erreur, résultat cohérent avec les listes/détails, accès au clavier et absence d’action interdite. Un défaut doit être décrit avec page/rôle, étapes et observation, sans données réelles. Ne pas cocher un rôle seulement parce que le menu s’affiche.

| Rôle | Serveur | Navigateur humain de bout en bout | Preuve/observation |
|---|---|---|---|
| Caissier | OK | OK déclaré utilisateur | confirmation du 4 novembre 2026 |
| Pharmacien | OK | OK déclaré utilisateur | confirmation du 4 novembre 2026 |
| Stock | OK | OK déclaré utilisateur | confirmation du 4 novembre 2026 |
| Gestion | OK | OK déclaré utilisateur | confirmation du 4 novembre 2026 |
| Administrateur | OK | OK déclaré utilisateur | confirmation du 4 novembre 2026 |

Entrée dans le terminal arrête le serveur et nettoie les données temporaires. Les compteurs HTTP ne constituent pas un verdict UX ; remplir le tableau à partir des observations. Lecteur d’écran, vitesse humaine et impression physique restent à tester séparément.

Empreinte du rapport serveur : `dcb74b1090a4fe8f9f172a51684ea0936af4e0bafd4cf1b56e6e9830ace44112`.

## Si la connexion échoue

Ouvrir exactement l’adresse annoncée dans le terminal de run_manual_review ; les comptes ux_* n’existent pas dans la base du serveur habituel. Le port change à chaque lancement. Ne pas appuyer sur Entrée dans le terminal avant la fin des essais. Si l’erreur persiste, relever l’URL et le message exact, jamais le mot de passe ; les refus CSRF (403) et un compte non reconnu ne sont pas la même cause. Un nouveau lancement recrée une base et des comptes indépendants des précédents.

## 4 novembre 2026 — Confirmation utilisateur

Après correction de l’adresse (utiliser le port du serveur fictif, pas le serveur habituel 8000), l’utilisateur confirme : « cette fois c’est ok j’ai tout testé c’est bon ». Les cinq parcours manuels sont donc enregistrés OK déclaré par l’utilisateur, en complément des 15/15 contrôles HTTP. Navigateur/version, dimensions et captures non transmis ; aucune mesure instrumentée supplémentaire ni conformité globale déduite. Cette confirmation ne remplace pas un lecteur d’écran, une mesure humaine de vitesse ou une impression physique.
