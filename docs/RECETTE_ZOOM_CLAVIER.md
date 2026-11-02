# Recette humaine : zoom, clavier et confirmation

Préparée le 2 novembre 2026. **Non exécutée** : nécessite un navigateur manipulé par l’utilisateur. Les 112 succès automatiques du rapport f2gyt6jp ne remplacent pas ces contrôles. Aucun résultat humain n’est précoché.

## 1. Ouvrir le serveur isolé

```bash
.venv/bin/python tools/run_manual_review.py --role administrateur
```

Saisir un mot de passe temporaire de huit caractères minimum, différent des mots de passe réels. Il est masqué et reste en mémoire. La préparation utilise la même base et les mêmes médias fictifs que la recette automatique, dans un répertoire temporaire ; les migrations s’appliquent uniquement à cette base. Aucun seed ni migration sur la base active.

Ouvrir l’adresse de connexion affichée, se connecter avec `ux_administrateur` et le mot de passe choisi. Ne pas utiliser le serveur habituel sur 8000/8001 : le lanceur annonce son propre port. Garder le terminal ouvert. Les liens affichés donnent accès à la caisse brouillon, au formulaire médicament et à l’inventaire.

Le journal conserve chemins et dates autorisées, pas les corps POST/cookies/mots de passe. Aucune réussite n’est déduite de son contenu. À la fin, Entrée dans le terminal arrête le serveur et nettoie la base/médias temporaires. Ctrl+C déclenche aussi le nettoyage normal ; éviter un arrêt forcé. Les observations et captures doivent être conservées séparément des données temporaires.

## 2. Premier passage à 1280 px

1. Régler le zoom navigateur à 100 %, choisir une fenêtre dont la zone de contenu mesure environ 1280 px de large. Noter navigateur/version, système, largeur initiale, rôle, thème et JS. Si une dimension exacte n’est pas possible, consigner la dimension réellement obtenue.
2. Ouvrir la vente brouillon dont le lien est affiché. Passer en thème sombre au pied de page.
3. Dans le menu du navigateur, choisir **200 %** et vérifier le pourcentage affiché. Ce test est un zoom de page réel, pas le zoom d’une capture ni le facteur d’échelle de la barre d’émulation mobile. Noter la largeur résultante si disponible : le nombre de CSS px visibles diminue normalement.
4. Vérifier que recherche, choix du produit/quantité, panier, montant total, ordonnance et paiement sont atteignables en faisant défiler. Aucun texte essentiel ni bouton ne doit être recouvert par le résumé de panier ou une barre collante. Le défilement interne d’un tableau est à distinguer d’un débordement de toute la page.
5. Sans souris, parcourir Tab et Maj+Tab : chaque arrêt est visible, l’ordre reste compréhensible, aucun piège hors dialogue. Tester F2 (recherche), F4 (encaissement), puis le lien d’évitement après rechargement. Ne pas activer Encaisser pour cette recette.
6. Ouvrir le formulaire médicament par le lien affiché. À 200 %, vérifier libellés, aides, progression et boutons. Soumettre l’étape vide via Continuer : erreur explicite et focus sur le champ concerné. Remplir les champs obligatoires et parcourir les étapes puis revenir ; ne pas enregistrer de fiche pour cette vérification.
7. Refaire en thème clair. Revenir à 100 % après chaque passage et contrôler visuellement le réglage.

Reproduire ensuite avec largeurs initiales 360, 768 et 1920 px quand le navigateur/écran le permet. Ne pas remplacer un cas impossible par un résultat supposé : noter « non exécuté » et la limite matérielle. L’émulation responsive peut compléter le test de reflow, mais ne suffit pas à prouver un zoom réel si le navigateur désactive ce réglage dans ce mode.

## 3. Dialogue d’inventaire : annulation au clavier

Dans le serveur fictif, ouvrir le lien `/stocks/.../inventaire/` annoncé. Lire la quantité actuelle et laisser le comptage et le blocage identiques ; remplir les champs obligatoires et la confirmation explicite éventuelle.

- Atteindre le bouton principal au clavier et l’activer : le dialogue doit expliquer l’effet sur comptage/blocage ; le bouton Revenir reçoit normalement le focus (autofocus du template).
- À 200 %, lire tout le dialogue et atteindre les deux boutons. Tab/Maj+Tab doivent rester dans le dialogue modal ; le contenu derrière ne doit pas être activable.
- Échap ferme le dialogue et restitue le focus au bouton déclencheur. Aucun message d’enregistrement ni navigation de succès ne doit apparaître.
- Réouvrir et activer Revenir au clavier : même résultat, saisie conservée. Ne pas activer Confirmer pour ce passage.
- Répéter clair/sombre. Sans JS, le dialogue enrichi n’existe pas : le formulaire natif et les confirmations serveur restent le repli ; ne pas déclarer un dialogue absent comme un défaut.

Ce parcours vérifie l’annulation ; il ne prouve ni la réussite ni l’idempotence d’un inventaire. Le retour navigateur et les doubles soumissions seront testés séparément sur données isolées.

## 4. Texte seul et preuves

Firefox : option « Zoom texte seulement » si disponible, puis 200 %. Pour un autre navigateur, noter le mécanisme exact d’agrandissement utilisé. Ne pas assimiler une augmentation du zoom de page à un agrandissement du texte seul. Vérifier de nouveau la caisse et les champs/boutons du formulaire. Si indisponible, marquer non exécuté.

En cas de défaut : capture incluant le problème, page/largeur/thème/zoom/JS, élément attendu et résultat observé. Ne jamais transmettre de mot de passe ni de capture de données réelles.

| Page | Largeur initiale/résultante | Thème | Zoom réellement affiché | JS | Résultat réel | Preuve ou limite |
|---|---|---|---|---|---|---|
| Caisse | 1280 / à relever | Sombre | à relever | oui | non exécuté | utilisateur requis |
| Formulaire médicament | 1280 / à relever | Sombre | à relever | oui | non exécuté | utilisateur requis |
| Dialogue inventaire (Échap/Revenir) | 1280 / à relever | Sombre | à relever | oui | non exécuté | utilisateur requis |

Ajouter les lignes des autres combinaisons testées. Le lecteur d’écran, les contrôles natifs ouverts et le zoom des autres familles restent des contrôles distincts.

Pour le premier retour, fournir : navigateur/version, zoom affiché, largeur initiale, puis pour chacun des trois parcours « OK », « KO + description » ou « non exécuté + raison ». Nous compléterons les autres combinaisons après ce premier passage.
