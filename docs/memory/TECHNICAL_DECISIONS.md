# Décisions techniques

Décisions reconstituées le 30 octobre 2026 depuis le code, les guides et l’historique accessible. Les dates d’origine ne sont pas toutes connues. Les propositions futures ne sont pas des décisions adoptées.

| Décision retenue | Justification et conséquence | Preuve |
|---|---|---|
| Une application métier Django `pharmacy` | Limiter le découpage artificiel ; séparation par modèles/formulaires/services/vues | `config/settings.py`, `pharmacy/`, `docs/CONCEPTION.md` |
| SQLite IMMEDIATE et mises à jour conditionnelles | Prévenir stock négatif et doubles sorties ; écritures concurrentes susceptibles d’être refusées temporairement | `settings.py`, `services.py`, tests de concurrence |
| Commande distincte de réception | Le stock représente les marchandises effectivement reçues ; livraisons partielles possibles | Purchase, Receipt et services |
| Stock matérialisé par lot avec mouvements | Mise à jour atomique et traçabilité ; préserver les deux dans toute mutation | Lot, StockMovement, services |
| FEFO et contrôle final serveur | Réduire les pertes ; disponibilité du panier indicative, non réservée | `add_sale_line`, `validate_sale` |
| Prix/coûts historiques et retours compensatoires | Conserver l’historique même après changement de prix ou remboursement | SaleLine, ReceiptLine, SaleReturn et tests |
| Jetons uniques réception/retour et statut de vente | Rendre les répétitions idempotentes ; ne pas dépendre du blocage du bouton JS | modèles/services/tests |
| Paiement intégral ; électronique vérifié manuellement | Aucune intégration prestataire fournie ; permission dédiée et référence obligatoires | Payment, CheckoutForm, validate_sale |
| Rôles cumulables via groupes Django | Contrôle fin serveur et affichage cohérent des actions ; pas d’isolation de tenant | setup_roles, vues/services/templates |
| Templates Django et JS progressif, ressources locales | Connexion faible, pas de build ni de dépendance CDN ; maintenir le repli sans JS | templates, static, documentation UI |
| Calculs UI en centimes BigInt | Éviter les erreurs de flottants ; estimations non comptables, serveur souverain | modules math JS et tests Node |
| Assistant en trois étapes pour médicament | Alléger le formulaire sans changer le POST ; toutes les sections accessibles sans JS | forms.js, form.html, test_ui.py |
| ReportLab avec repli PDF texte | Dépendance non installable lors du travail hors réseau ; repli utilisable mais rendu ReportLab à vérifier séparément | pdf.py, README |
| Archivage et FK PROTECT | Préserver l’historique ; catégorie utilisée non supprimable | modèles, entity_delete, tests |
| Sauvegarde cohérente et restauration vers nouveau fichier | Éviter l’écrasement de la base active ; bascule explicite après contrôle | commandes backup_db/restore_db, tests |

## Choix différés

PostgreSQL, multi-tenant, passerelle de paiement, vrai mode hors ligne, scanner caméra, thème sombre et personnalisation des raccourcis ne sont pas livrés comme fonctionnalités validées. Le thème sombre n’est pas nécessaire à la reprise de la refonte actuelle. Toute introduction de SaaS rizicole nécessiterait un nouveau périmètre.

## Contraintes d’environnement rencontrées

- `.git` a été en lecture seule pour l’agent : préparation de branches/fusions en copie temporaire et bundles, puis application par l’utilisateur. Vérifier Git actuel, ne pas rejouer les scripts aveuglément.
- Port de développement déjà utilisé : résolu côté utilisateur, serveur indiqué ensuite sur 8001 ; port actuel à vérifier.
- Recette navigateur antérieure bloquée par le sandbox et les accès locaux ; script disponible mais aucune validation visuelle complète déduite de sa présence.

Ces contraintes sont historiques, pas des hypothèses permanentes sur les futures sessions.

## 30 octobre 2026 — Temporalité du dashboard

Séparer visuellement les alertes/indicateurs actuels de l’analyse datée. Réutiliser le formulaire GET et le contexte existant ; aucune comparaison de tendance sans données correspondantes. Navigation par ancres et filtres natifs utilisables sans JavaScript. Conséquence : amélioration limitée à la présentation, sans nouveau calcul métier.

## 30 octobre 2026 — Lecture des stocks

Conserver le filtre GET serveur et le tri `expires_on, pk` ; les raccourcis de statut gardent la recherche et retirent la page. Distinguer quantité physique, péremption et blocage sans créer de nouveau calcul de disponibilité : les contrôles de délivrance restent à la caisse. Pas de stockage navigateur, de tri local trompeur ni de nouvelle vue. Aide en `details` natif et permissions existantes préservées.
