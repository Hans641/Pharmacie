#!/usr/bin/env python3
"""Recette humaine sur données fictives temporaires, sans base active ni secret journalisé."""
import argparse
import getpass
import json
from pathlib import Path
import sys
import tempfile
import threading
from run_ux_review import prepare
from ux_review_server import create_server, RequestJournal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--role', choices=['administrateur', 'pharmacien', 'caissier', 'stock', 'gestion', 'all'], default='administrateur')
    args = parser.parse_args()
    if not sys.stdin.isatty():
        parser.error('Lancer dans un terminal interactif : mot de passe temporaire saisi sans affichage.')
    password = getpass.getpass('Choisis un mot de passe temporaire de recette (8 caractères minimum) : ')
    if len(password) < 8:
        parser.error('Mot de passe temporaire trop court.')
    with tempfile.TemporaryDirectory(prefix='pharmagest-manual-data-') as directory:
        cases = prepare(Path(directory), password)
        selected = [case for case in cases if args.role in ['all', case['role']]]
        from django.contrib.staticfiles.handlers import StaticFilesHandler
        from django.core.wsgi import get_wsgi_application
        output = Path(tempfile.mkdtemp(prefix='pharmagest-manual-report-'))
        journal = RequestJournal(output / 'requests.jsonl')
        with create_server(StaticFilesHandler(get_wsgi_application()), 'threaded', journal) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f'http://127.0.0.1:{server.server_port}'
                print('Recette isolée, données fictives. Base active et médias actifs non utilisés.')
                print('Connexion : ' + base + '/comptes/login/')
                print('IMPORTANT : les comptes ux_* existent uniquement à cette adresse de recette, pas sur le serveur habituel 8000/8001.')
                print('Un redémarrage change le port et recrée les comptes. Garde ce terminal ouvert ; Entrée arrête le serveur.')
                print('Mot de passe : celui saisi au démarrage, identique pour les comptes fictifs ; aucun mot de passe journalisé.')
                for case in selected:
                    print('Rôle : ' + case['role'] + ' — utilisateur : ' + case['username'])
                    routes = case['routes'] + ([f'/ventes/{case["sale_id"]}/'] if case['sale_id'] else [])
                    if case['wizard']:
                        routes.append('/catalogue/medicaments/ajouter/')
                    for route in routes:
                        print(base + route)
                print('Protocole : docs/RECETTE_ROLES.md' if args.role == 'all' else 'Protocole : docs/RECETTE_ZOOM_CLAVIER.md')
                print('Rapport local : ' + str(output))
                input('Laisse ce terminal ouvert pendant les essais. Entrée pour arrêter et nettoyer les données : ')
            finally:
                journal.record('cleanup_started')
                server.close_clients()
                server.shutdown()
                thread.join(timeout=5)
                (output / 'summary.json').write_text(json.dumps({
                    'mode': 'manual', 'role': args.role,
                    'result': 'non évalué : observations humaines à renseigner',
                    'http': journal.summary(),
                }, ensure_ascii=False, indent=2) + '\n')
                print('Serveur arrêté ; aucune réussite UX déduite des requêtes. Rapport : ' + str(output))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nArrêt demandé.')
