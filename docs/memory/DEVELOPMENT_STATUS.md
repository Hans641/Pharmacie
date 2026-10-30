# État du développement

Dernière vérification : **30 octobre 2026**. Code analysé à `main` / `c3026db` ; référence locale `origin/main` identique lors de l’inspection. Cela ne prouve pas à lui seul l’état distant en temps réel.

## Fonctions implémentées et preuves disponibles

| Ensemble | Preuves | Limites |
|---|---|---|
| Auth, rôles, comptes, CSRF, accès | vues/formulaires/setup_roles ; InterfaceTests et tests de permissions | SMTP réel et protection anti-bruteforce non validés |
| Catalogue, catégories, fournisseurs, clients, photos et archivage | modèles/forms/entity_* ; tests images, recherche, historique et accès | Pas de recette utilisateur complète attestée |
| Achats et réceptions partielles | services et tests reliquat, rollback, réception unique | Écran de réception par ligne ; service accepte plusieurs lignes |
| Lots, FEFO, inventaire et mouvements | services, BusinessTests | PostgreSQL et forte charge non testés |
| Vente, paiement intégral, ordonnance, concurrence | tests atomicité, stock, historique, double validation et concurrence | Électronique manuel ; pas de réservation globale des brouillons |
| Retours et remise en stock contrôlée | tests quantité, idempotence, lot périmé et historique | Remboursement exécuté hors logiciel |
| Dashboard et PDF | code de calcul, tests de rendu et signature PDF | Rendu visuel PDF/ReportLab et conformité fiscale non établis |
| Sauvegarde/restauration SQLite | BackupTests | Test isolé ; pas de reprise de production attestée |
| Design system, composants, navigation et formulaires progressifs | templates/static, PresentationTests et ProgressiveFormTests | WCAG AA et quatre largeurs non certifiées |
| Prévisualisations réception/inventaire/retour | OperationPresentationTests, 9 tests JS | Estimations ; validation métier serveur |
| Caisse améliorée | CashierExperienceTests, 12 tests JS ; fusion c3026db | Temps de vente <30 s et usage matériel non mesurés |

## Vérifications de la session documentaire précédente

Environnement : Python 3.12.3, Django 6.0.4, ReportLab absent.

- `.venv/bin/python manage.py test --verbosity 1` : **79 tests réussis**, 158,296 s ; base de test créée puis détruite.
- `.venv/bin/python manage.py check` : aucune anomalie signalée.
- `.venv/bin/python manage.py makemigrations --check --dry-run` : aucun changement détecté ; aucune migration créée ou appliquée.
- `node tools/cashier_math.test.mjs` : **12 réussis**.
- `node tools/operation_math.test.mjs` : **9 réussis**.

Les tests PDF vérifient notamment réponse, type et signature ; ils ne prouvent pas la lisibilité des documents. Les tests de concurrence SQLite acceptent des refus temporaires et contrôlent l’absence de double sortie/stock négatif ; ils ne constituent pas un test de charge ni une preuve de verrouillage de ligne.

## Dernière étape et travail actuel

La refonte caisse est commitée (`c6ec3c6`) et fusionnée (`c3026db`). L’itération précédente formulaires/opérations est fusionnée (`6a5426f`). La mémoire persistante est créée. Reprise UI : clarification du tableau de bord (temporalité, navigation interne, filtres et limites des aperçus) dans le template et le CSS uniquement ; voir `../RECETTE_DASHBOARD.md`. Le commit et la fusion sont autorisés pour cette tâche. Préparation en copie isolée, car la création de branche dans le dépôt actif échoue (`.git` en lecture seule). Application à `main` à confirmer après exécution du finaliseur côté utilisateur ; aucun push prévu.

## Prochaines étapes prioritaires

1. Recette réelle de caisse sur données isolées, aux largeurs 360, 768, 1280 et 1920 px : clavier, focus, mobile, erreurs, paiement, ordonnance, impression et absence de double soumission. Suivre `../RECETTE_CAISSE.md` et `../RECETTE_UX.md` ; documenter les résultats plutôt que supposer la réussite.
2. Mesurer plusieurs ventes fictives représentatives et vérifier l’objectif de 30 secondes.
3. Après la recette du dashboard clarifié, poursuivre les stocks/listes, après inspection des améliorations déjà présentes. Comparer au plan `../AUDIT_UX.md` et ne pas refaire les composants existants.
4. Avant exploitation : SMTP, HTTPS/serveur WSGI, protection des tentatives de connexion, supervision, sauvegardes hors machine, validation locale des documents/procédures ; voir `../EXPLOITATION.md`.

## Non réalisé ou incertain

Pas de multi-tenant, SaaS rizicole, paiement partiel, intégration prestataire, comptabilité générale, prescription automatique, mode hors ligne complet ou scanner caméra. Pas de validation navigateur complète, de conformité WCAG 2.2 AA attestée, de certification fiscale ni de déploiement de production démontré. Le fonctionnement des ressources locales n’implique pas une application hors ligne.

## Itération UI — tableau de bord, 30 octobre 2026

- Situation actuelle et période analysée distinguées ; filtres datés explicites, retour au mois en cours, liens de section et limites des aperçus.
- Aucun changement de vue, calcul, permission, modèle ou migration. Recette navigateur aux quatre largeurs encore à exécuter.
- Vérification ciblée : résultats consignés dans SESSION_LOG ; les 79 tests ci-dessus concernent la session documentaire précédente.

## Recette et intégration — 30 octobre 2026

- `DashboardPeriodTests` ajoute trois tests : distinction période/données actuelles, dates inversées, affichage pour les cinq rôles et sans permissions. Le gestionnaire de stock conserve le filtre des achats sans voir les chiffres des ventes.
- Le script navigateur couvre maintenant les ancres au clavier, la période passée, le retour au mois courant et les filtres sans JavaScript. Exécution complète non réalisée : Chrome échoue avant rendu avec `setsockopt: Operation not permitted` ; Playwright Node n'est pas installé dans le projet.
- Les 21 tests JS restent réussis ; syntaxe du script navigateur, check Django et absence de changement de migration vérifiés.
- Intégration préparée sur `feat/dashboard-clarity` dans une copie isolée, avec fusion sans fast-forward. Le bundle et le finaliseur sous `.publication/` sont locaux et ignorés. Ils ne signifient pas que le dépôt actif ou GitHub a été modifié. Référence du dépôt actif lors de la préparation : `c3026db`.

Validation finale de cette itération : **82 tests Django réussis en 153,801 s**, **21 tests JS réussis**, `manage.py check` sans anomalie, `makemigrations --check --dry-run` sans changement, `node --check tools/ux_browser_check.cjs` et `git diff --check` réussis. Recette navigateur non validée pour les raisons ci-dessus.
