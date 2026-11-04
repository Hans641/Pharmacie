# Accessibilité approfondie — 4 novembre 2026

## État mesuré

Main initialement propre à 2c02668, fusion du bilan précédent confirmée. Aucun défaut applicatif démontré dans cette étape. Nouveau audit HTML exécuté : `.venv/bin/python tools/run_semantic_review.py` ; rapport `/tmp/pharmagest-semantic-report-kx3q74uq/summary.json`, **50/50 rendus HTML OK** : 45 pages des cinq rôles, trois formulaires vides invalides et deux pages anonymes.

L’outil vérifie présence de main/H1/langue/lien d’évitement, unicité des IDs, cibles aria-labelledby/describedby/controls, noms HTML identifiés des contrôles et attribut alt des images. Les témoins unitaires négatifs détectent bien contrôle sans nom, cible ARIA manquante et ID dupliqué ; témoin positif labels explicites/implicites/aria-label accepté : **4/4 tests réussis**. Check Django, compilation et diff sans anomalie. Aucun test Django complet relancé pour ces seuls outils/docs.

Limites : parseur de HTML source, pas moteur du nom accessible, ni arbre d’accessibilité Chromium/Firefox, ni contraste, géométrie, états JS ou parole. Les enfants masqués/états dynamiques ne sont pas simulés. Aucun score WCAG n’est produit. Les contrôles métier des formulaires vides n’ont créé ni médicament, ni vente, ni mouvement de stock.

Orca 46.1 présent sur le poste ; Firefox est installé via snap. La commande Firefox de l’agent échoue sur XDG_RUNTIME_DIR en lecture seule. **Aucun navigateur graphique ni lecteur d’écran piloté/écouté par l’agent**. Le test vocal doit être réalisé dans la session graphique utilisateur.

## Premier passage humain : trois scénarios

Lancer le serveur isolé et laisser son terminal ouvert :

```bash
.venv/bin/python tools/run_manual_review.py --role administrateur
```

Choisir un mot de passe temporaire. Ouvrir Firefox depuis la session graphique et saisir exactement l’URL « Connexion : » affichée (port variable, pas le serveur habituel). Activer Orca depuis les applications ou les réglages d’accessibilité du bureau, puis se connecter avec ux_administrateur et ce mot de passe temporaire. Ne pas partager le mot de passe ni un enregistrement vocal qui le contiendrait. Aucun compte de recette sur la base habituelle.

Noter version du navigateur, Orca, thème, zoom et largeur approximative. Premier passage desktop 1280 px, thème clair et zoom 100 %, puis variante sombre/mobile et texte seul si disponible. La confirmation antérieure des parcours métier ne vaut pas test au lecteur d’écran.

### A. Repères et caisse

1. Après rechargement, utiliser Tab et le lien Aller au contenu : vérifier que la lecture atteint le contenu principal et que la page/titre est identifiable.
2. Ouvrir le brouillon fictif annoncé. Parcourir tous les contrôles avec Tab et Maj+Tab ; relever les éléments non nommés, répétés inutilement ou inatteignables. Le focus doit rester visible à chaque étape.
3. Vérifier que recherche, médicament, quantité, tableau/panier, lot, total, mode de paiement et confirmation ont un nom intelligible. Explorer les titres et le tableau avec les commandes de navigation du lecteur.
4. F2 puis F4 : vérifier que le changement de focus est annoncé de façon compréhensible. Les seuls repères visuels ne suffisent pas.
5. Saisir un montant reçu supérieur au total fictif. Écouter la mise à jour de la monnaie : annoncée sans déplacer le focus et sans interruption en boucle. Ne pas encaisser pour ce passage.

Attendu : noms et valeurs exploitables, contexte du lot/ordonnance accessible, total retrouvable, ordre cohérent. Noter les paroles réellement entendues ; la présence de aria-live dans le HTML ne prouve pas l’annonce.

### B. Erreur et progression du formulaire médicament

1. Ouvrir le formulaire d’ajout de médicament à partir du lien affiché, avec le compte administrateur.
2. Activer Continuer sans saisir le nom. Écouter le libellé, le caractère obligatoire et l’erreur, et vérifier le focus sur le champ à corriger.
3. Renseigner les champs obligatoires de la première étape et continuer. L’étape et son titre doivent rester compréhensibles vocalement ; les champs de l’étape masquée ne doivent pas interrompre le parcours Tab.
4. Revenir à l’étape précédente : valeur conservée et progression intelligible. Ne pas enregistrer la fiche.

Les erreurs serveur et le résumé peuvent être testés en complément sans JS sur données fictives ; ne pas compter une erreur locale seule comme preuve de toutes les erreurs serveur.

### C. Dialogue d’inventaire

1. Ouvrir l’inventaire annoncé, garder la quantité actuelle et renseigner un motif fictif et les confirmations requises.
2. Activer le bouton principal : le dialogue doit être annoncé avec son titre et sa description ; vérifier le focus sur Revenir.
3. Tab/Maj+Tab : le focus reste dans le dialogue, les éléments derrière ne sont pas activables. Échap ferme le dialogue et restitue le focus au déclencheur.
4. Réouvrir, puis choisir Revenir. Même résultat et saisie conservée ; ne pas activer Confirmer pour cette recette.

## Texte seul et zoom restant

Suivre aussi RECETTE_ZOOM_CLAVIER.md. Dans Firefox, utiliser son option de zoom texte seulement lorsqu’elle est disponible, puis 200 % ; relever le réglage effectivement appliqué. Vérifier caisse, champs, erreurs, progression et dialogue : aucun texte essentiel masqué ou chevauché, boutons atteignables. Refaire en zoom de page réel 200 %, séparément. Une émulation de viewport ou un changement de résolution ne suffit pas à prouver ces essais.

## Résultats à transmettre

| Scénario | Navigateur/Orca, thème, zoom, largeur | Annonces et clavier | Résultat réel |
|---|---|---|---|
| Repères/caisse/monnaie | à relever | à relever | non exécuté |
| Formulaire/erreurs/progression | à relever | à relever | non exécuté |
| Dialogue/Échap/Revenir | à relever | à relever | non exécuté |
| Texte seul 200 % | à relever | à relever | non exécuté |

Pour le premier retour, commencer par les trois scénarios : OK, KO avec étape et annonce observée, ou non exécuté avec raison. Ne pas attribuer un échec au lecteur ou au navigateur avant de relever le problème précis. Les autres familles restent hors de cette première passe ; aucune conformité globale attestée.

Empreinte rapport HTML : `725e4ac097720c53cb366707e9806670ddcdfea9c535cca9669d3c9a7cfa2f49`.

Le 4 novembre, l’utilisateur indique les essais effectués et demande le point suivant. Versions, annonces et verdicts détaillés non transmis : statut « déclaré effectué », sans validation globale ni mesure supplémentaire. Le point suivant est le chronométrage humain décrit dans RECETTE_CAISSE.md.
