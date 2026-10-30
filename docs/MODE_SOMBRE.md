# Thèmes clair et sombre — 30 octobre 2026

## Utilisation et couverture

Choisir **Système**, **Clair** ou **Sombre** dans le sélecteur de thème en pied de page. Le réglage système fonctionne aussi sans JavaScript via `prefers-color-scheme`. Une préférence manuelle est mémorisée sous la seule clé `pharmagest-theme` ; aucun identifiant ni donnée métier. Si le stockage est interdit, la bascule reste active sur la page courante. Les onglets se synchronisent lorsque le stockage est disponible.

Toutes les pages héritant de `base.html` sont couvertes : tableau de bord, caisse, catalogue et fiches, stocks, achats/réceptions, inventaires/retours, ventes, rapports, mouvements, audit, utilisateurs, connexion et gestion du mot de passe. Les e-mails texte et les PDF ont leur propre présentation. L'administration Django conserve son thème natif.

## Fichiers et choix

- `static/css/app.css` : couleurs auparavant figées remplacées par des tokens ; boutons et barre de caisse séparent fond d'action et couleur de texte.
- `static/css/experience.css` : bordures de progression et squelettes utilisent ces tokens.
- `static/css/themes.css` : palette sombre à l'écran, préférence système/manuelle, contrôles natifs et Bootstrap, meter, états des boutons, sélecteur de thème.
- `static/js/theme.js` : application de la préférence avant le rendu principal, mémorisation et synchronisation. Aucun appel réseau.
- `templates/base.html`, `templates/includes/theme_control.html` : ressources locales et sélecteur partagé accessible au clavier.
- `static/css/print.css` : impression claire ; largeur minimale de catalogue supprimée pour le papier. Les variables sombres sont limitées à l'écran.

Aucune inversion globale des couleurs : photographies et icônes restent intactes. Texte clair sur fonds vert sombre/gris, accents pharmacie, et états succès/alerte/danger/info distincts avec leurs libellés existants. Aucune modification des permissions ou des validations métier.

## Contrastes calculés

Valeurs théoriques des tokens sRGB, pas une certification de chaque composition affichée :

| Texte / fond | Clair | Sombre |
|---|---:|---:|
| `--ink` / `--bg` | 13.51:1 | 15.37:1 |
| `--ink` / `--surface` | 14.57:1 | 13.33:1 |
| `--muted` / `--surface` | 6.07:1 | 8.39:1 |
| `--muted` / `--surface-soft` | 5.43:1 | 6.86:1 |
| `--green` / `--surface` | 6.86:1 | 9.94:1 |
| `--green-dark` / `--surface-soft` | 9.30:1 | 9.98:1 |
| `--on-primary` / `--primary-bg` | 6.86:1 | 11.20:1 |
| `--on-primary` / `--primary-hover` | 10.40:1 | 12.93:1 |
| `--success` / `--success-bg` | 6.94:1 | 8.13:1 |
| `--warning` / `--warning-bg` | 7.15:1 | 9.18:1 |
| `--danger` / `--danger-bg` | 6.69:1 | 7.90:1 |
| `--info` / `--info-bg` | 6.99:1 | 8.29:1 |
| `--table-ink` / `--surface` | 10.33:1 | 13.33:1 |
| `--table-head-ink` / `--table-head` | 8.09:1 | 9.33:1 |
| `--placeholder` / `--surface` | 5.27:1 | 8.39:1 |
| `--nav-ink` / `--surface` | 8.98:1 | 11.41:1 |
| `--green-dark` / `--nav-selected` | 8.76:1 | 7.75:1 |

Focus et bordure des champs : au moins 3:1 sur la surface dans les deux palettes. États désactivés, superpositions et captures réelles restent à inspecter.

## Recette manuelle restante

1. Tester les trois choix sur chaque famille de pages, à 360, 768, 1280 et 1920 px.
2. Vérifier le changement de préférence système, la navigation entre pages, le rechargement, la synchronisation des onglets et le stockage indisponible.
3. Vérifier champs et options, calendriers natifs, photo, cases/radios, validation locale/serveur, erreurs, confirmation, menus et focus clavier.
4. Vérifier le total et les modes de paiement, les badges de stock et les chiffres du dashboard.
5. Sans JS : le thème système s'applique ; aucun sélecteur inopérant n'est présenté.
6. Aperçu d'impression depuis un écran sombre : fond clair, tableaux complets, aucune commande de thème. Vérifier séparément les PDF.

La recette navigateur générale est toujours incomplète : le dernier rapport `6zmmb904` signale un bouton de période instable lors d'un clic automatisé. Ce résultat diffère du précédent arrêt sur l'assistant médicament. La demande utilisateur a réorienté le travail vers les thèmes ; ne pas considérer ces incidents comme résolus ni le thème sombre comme validé visuellement.
