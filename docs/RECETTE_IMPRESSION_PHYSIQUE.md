# Impression physique — 4 novembre 2026

## État réel

Les onze documents ReportLab et leurs 23 pages ont été générés et examinés à l’écran le 3 novembre (RECETTE_PDF.md). Cela ne prouve pas une impression sur papier. Au 4 novembre : `lpstat -r` indique scheduler is not running, `lpstat -d` indique no system default destination. Aucun travail d’impression envoyé. Les anciens PDF et le venv de recette sous /tmp ont disparu ; ReportLab est absent de .venv. **Recette physique non exécutée**, aucune conformité fiscale déduite.

## Régénérer les documents fictifs

Depuis la racine du dépôt, recréer l’environnement séparé s’il a disparu :

```bash
python3 -m venv /tmp/pharmagest-pdf-env-hote
/tmp/pharmagest-pdf-env-hote/bin/python -m pip install -r requirements.txt
/tmp/pharmagest-pdf-env-hote/bin/python tools/run_pdf_review.py
```

Utiliser uniquement le dossier annoncé par ce nouveau lancement. Ce script crée base/médias temporaires et documents fictifs ; il ne lance aucune impression. Les comptes ux_* du serveur manuel ne sont pas nécessaires pour ouvrir ces PDF.

## Premier passage papier

Depuis le lecteur PDF du poste qui dispose de l’imprimante, choisir explicitement l’imprimante réelle et noter modèle, format papier, orientation, échelle et recto/verso. Les PDF actuels sont en A4 paysage ; commencer sur A4 avec l’échelle réelle, sans supposer qu’un pilote respecte automatiquement ce format.

Imprimer :

1. `recu.pdf` : référence, article, lot, quantité, prix unitaire, total et pied de page lisibles. Comparer valeurs au PDF à l’écran. La mention Démonstration doit être conservée pour ces données fictives.
2. `commande.pdf` ou `reception.pdf` : colonnes et montants dans les marges, accents lisibles, aucun bord coupé.
3. `long-vente.pdf` : toutes les pages, en-têtes répétés, numéros cohérents, lignes 001 à 080 présentes une seule fois et total final lisible. Les valeurs de cette fixture ne correspondent pas à une opération commerciale réelle.

Vérifier également contraste en niveaux de gris, petits textes du pied, pli/coupe éventuels et ordre des feuilles. Une feuille presque vide contenant une dernière ligne valide n’est pas une perte de ligne ; la pagination réelle doit rester cohérente.

## Si une imprimante thermique est prévue

Noter largeur réelle (ex. 58/80 mm) et pilote, puis examiner l’aperçu et une sortie d’essai. Les documents actuels sont des PDF A4 paysage : **aucune mise en page de ticket thermique dédiée n’est validée**. Une réduction automatique qui rend les montants illisibles est un KO. Un format thermique spécifique sera un travail de présentation distinct à définir avec la largeur et le matériel réels, sans modifier les calculs.

## Bilan à renseigner

| Document / matériel | Réglages | Texte et montants | Marges/coupes | Pages et lignes | Verdict |
|---|---|---|---|---|---|
| Reçu A4 | à relever | à relever | à relever | à relever | non exécuté |
| Commande/réception A4 | à relever | à relever | à relever | à relever | non exécuté |
| Vente de 80 lignes | à relever | à relever | à relever | à relever | non exécuté |
| Ticket thermique, si prévu | à relever | à relever | à relever | à relever | non exécuté |

Transmettre modèle/format, document et défaut précis si KO. Ne pas joindre de données réelles. Ce point peut rester ouvert si aucun matériel n’est disponible ; l’enregistrement Git des outils et protocoles ne constitue pas une réussite papier.
