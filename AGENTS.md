# Instructions permanentes — PharmaGest

## Identité et sources

Ce dépôt est **PharmaGest**, une application Django de pharmacie. Il ne contient pas un SaaS rizicole Laravel : pas d’Eloquent, de contrôleurs Laravel ni de multi-tenant. Ne pas introduire ces concepts à partir d’une demande générique sans clarifier un changement de périmètre.

Le code et les migrations actuels font foi. Le périmètre est défini par `Cahier des charges projet pharmacie.pdf` ; `docs/CONFORMITE.md` en donne la correspondance, à vérifier dans le code. Ne jamais considérer une fonctionnalité comme terminée sur la seule base de sa documentation.

## Reprendre une session

1. Lire ce fichier, puis `docs/memory/PROJECT_CONTEXT.md` et `DEVELOPMENT_STATUS.md`.
2. Consulter `ARCHITECTURE.md`, `TECHNICAL_DECISIONS.md` et les dernières entrées de `SESSION_LOG.md` selon la tâche.
3. Vérifier `git status --short --branch`, les derniers commits et les fichiers concernés. Préserver les changements existants.
4. Identifier la dernière étape réellement réalisée et ses preuves avant de reprendre. Ne pas réimplémenter une fonction présente.

Ces fichiers sont une mémoire du dépôt, pas une garantie de chargement automatique de tous leurs contenus par chaque outil. Les lire explicitement si nécessaire.

## Conventions et invariants

- Architecture Django MVT : modèles, formulaires, services transactionnels, vues, templates. Pas de framework front ni de compilation requis.
- Interface française, ariary à deux décimales (`15 000,00 Ar`), fuseau `Indian/Antananarivo` ; préserver les prix historiques.
- Les mutations de stock et transactions commerciales passent par `pharmacy/services.py`. Les créations et modifications de fiches restent dans les vues/formulaires existants.
- Préserver les permissions serveur, les contrôles `perms.*` des templates, CSRF et validations Django ; masquer une action ne remplace pas le contrôle serveur.
- Réception et encaissement atomiques, stock non négatif, FEFO, exclusion des lots bloqués/périmés, idempotence et traçabilité sont obligatoires.
- Aucun paiement électronique automatique : vérification externe manuelle par utilisateur habilité. Les remboursements sont exécutés hors application puis référencés.
- JavaScript vanille progressif, ressources locales, fonctionnement sans JS. Réutiliser les includes et tokens CSS. Focus visible, clavier, cibles de 44 px et information explicite au-delà de la couleur ; vérifier avant de revendiquer une conformité.
- En refonte UI, ne pas modifier modèles, migrations, vues, services ou permissions sans nécessité expliquée et périmètre autorisé.

## Sécurité et autorisations

- Ne jamais consigner de mot de passe, token, secret ou donnée personnelle réelle dans la mémoire, les journaux partagés ou Git. Ne pas recopier les valeurs d’environnement.
- Préserver la base active, les médias, fichiers locaux et travaux de l’utilisateur ; ne pas supprimer de données ou exécuter de migration destructive sans autorisation explicite.
- Ne pas modifier les migrations existantes pour changer un schéma déjà appliqué ; créer une migration adaptée après analyse.
- Ne pas exécuter `seed_demo`, `setup_roles`, une restauration ou une migration sur la base active pour une simple inspection documentaire.
- Pas de commit, fusion ni push sans autorisation pour la tâche concernée. Une autorisation d’une tâche passée n’autorise pas les suivantes. Pas de push forcé ni de contournement des restrictions du système de fichiers.
- Vérifier les droits réels à chaque session : `.git` a été en lecture seule lors de sessions antérieures. Les bundles sous `.publication/` sont des artefacts locaux, pas la source de vérité de l’état Git.

## Vérification

Utiliser l’environnement existant :

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test
node tools/operation_math.test.mjs
node tools/cashier_math.test.mjs
```

Choisir les contrôles utiles au changement ; les tests Django utilisent une base de test distincte. Un rendu du client de test ne prouve pas le comportement navigateur. La recette responsive/clavier et les mesures de temps sont décrites dans `docs/RECETTE_UX.md` et `docs/RECETTE_CAISSE.md`. Ne pas valider une vente ou réception réelle pour une recette : utiliser des données de test isolées.

## Entretenir la mémoire

Après chaque tâche importante : mettre à jour `DEVELOPMENT_STATUS.md`, consigner les nouvelles décisions dans `TECHNICAL_DECISIONS.md` et ajouter une entrée synthétique datée dans `SESSION_LOG.md`. Modifier `ARCHITECTURE.md` seulement si l’architecture change ; actualiser le contexte si le périmètre change.

Indiquer les fichiers/preuves, commandes et résultats disponibles ; distinguer réalisé, vérifié, proposé et incertain. Ne pas dupliquer les guides existants ni transformer des objectifs en résultats. Dater les constats susceptibles de changer. Ne pas stocker de longues conversations ou sorties de commande.
