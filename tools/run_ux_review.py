#!/usr/bin/env python3
"""Recette navigateur sur base et médias temporaires, sans secret persistant."""
import argparse
from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import uuid
from datetime import timedelta
from ux_review_server import create_server, RequestJournal

ROOT = Path(__file__).resolve().parent.parent


def playwright_module():
    """Réutiliser une installation locale ; aucune installation réseau implicite."""
    override = os.environ.get('PLAYWRIGHT_MODULE_PATH')
    if override:
        return override
    result = subprocess.run(['node', '-p', "require.resolve('playwright')"], cwd=ROOT,
                            capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    cached = Path.home() / '.cache/ms-playwright-go'
    for package in sorted(cached.glob('*/package'), reverse=True):
        if (package / 'package.json').is_file():
            return str(package)
    raise RuntimeError('Playwright absent. Installer dans un dossier de test : '
                       'npm install --prefix /tmp/pharmagest-browser playwright ; '
                       'puis définir PLAYWRIGHT_MODULE_PATH=/tmp/pharmagest-browser/node_modules/playwright. '
                       'Définir CHROME_PATH si Chrome est déjà installé.')


def prepare(work, password):
    # L'environnement est remplacé avant le premier import Django/config.settings.
    os.environ.update(DJANGO_SETTINGS_MODULE='config.settings',
                      DATABASE_PATH=str(work / 'review.sqlite3'), DJANGO_DEBUG='1',
                      DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost,testserver',
                      DEMO_PASSWORD=password)
    sys.path.insert(0, str(ROOT))
    import django
    django.setup()
    from django.conf import settings
    settings.MEDIA_ROOT = work / 'media'
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    from django.core.management import call_command
    from django.contrib.auth.models import User, Group
    from django.test import Client
    from django.utils import timezone
    from pharmacy.models import Medicine, Lot, Sale, Purchase
    from pharmacy import services

    assert Path(settings.DATABASES['default']['NAME']).resolve() == work / 'review.sqlite3'
    # seed_demo affiche normalement un mot de passe : sa sortie reste en mémoire.
    with redirect_stdout(StringIO()):
        call_command('migrate', verbosity=0, interactive=False)
        call_command('seed_demo', stdout=StringIO())
    roles = [
        ('administrateur', 'Administrateur'), ('pharmacien', 'Pharmacien responsable'),
        ('caissier', 'Caissier'), ('stock', 'Gestionnaire de stock'),
        ('gestion', 'Responsable de gestion'),
    ]
    cases = []
    med = Medicine.objects.get(barcode='9900000000000')
    med.name = 'Médicament fictif avec une dénomination volontairement longue pour contrôler le retour à la ligne et la lisibilité sur mobile'
    med.requires_prescription = True
    med.save()
    blocked = Lot.objects.filter(quantity__gt=0, expires_on__gt=timezone.localdate()).exclude(medicine=med).first()
    services.adjust_stock(User.objects.get(username='demo_admin'), blocked.pk,
                          blocked.quantity, 'Blocage fictif de recette UX', True)
    empty = Lot.objects.get(number='DEMO-007')
    services.adjust_stock(User.objects.get(username='demo_admin'), empty.pk,
                          0, 'Comptage fictif : lot épuisé', False)
    # Une réception partielle apporte un reliquat et un formulaire testable.
    purchase = Purchase.objects.get(status='draft')
    services.order_purchase(User.objects.get(username='demo_admin'), purchase.pk)
    line = purchase.lines.first()
    services.receive_purchase(User.objects.get(username='demo_admin'), purchase.pk, [{
        'line_id': line.pk, 'quantity': 1, 'number': 'UX-PARTIEL',
        'expires_on': timezone.localdate() + timedelta(days=365),
    }], uuid.uuid4())
    for slug, role in roles:
        user = User.objects.create_user('ux_' + slug, password=password,
                                        first_name='Préparatrice de démonstration au nom volontairement long')
        user.groups.add(Group.objects.get(name=role))
        routes = ['/', '/catalogue/medicaments/', '/stocks/', '/rapports/']
        if user.has_perm('pharmacy.view_purchase'):
            routes += ['/achats/', f'/achats/{purchase.pk}/']
        sale_id = None
        if user.has_perm('pharmacy.view_sale'):
            routes.append('/ventes/')
            sale = Sale.objects.create(author=user)
            services.add_sale_line(User.objects.get(username='demo_admin'), sale.pk, med, 1)
            sale_id = sale.pk
        if user.has_perm('pharmacy.receive_purchase'):
            routes.append(f'/achats/{purchase.pk}/reception/')
        if user.has_perm('pharmacy.adjust_stock'):
            routes.append(f'/stocks/{blocked.pk}/inventaire/')
        client = Client()
        client.force_login(user)
        checks = routes + ([f'/ventes/{sale_id}/'] if sale_id else [])
        wizard = user.has_perm('pharmacy.add_medicine')
        if wizard:
            checks.append('/catalogue/medicaments/ajouter/')
        for route in checks:
            response = client.get(route)
            if response.status_code != 200:
                raise RuntimeError(f'Préparation {slug} : {route} retourne {response.status_code}')
        cases.append(dict(role=slug, username=user.username, routes=routes,
                          sale_id=sale_id, wizard=wizard, rendered=len(checks)))
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true', help='Vérifier les données et rendus serveur sans ouvrir de navigateur.')
    parser.add_argument('--diagnose-lot1', action='store_true', help='Reproduire les deux échecs avec événements, géométrie et captures.')
    parser.add_argument('--probe-browser', action='store_true', help='Bouton témoin sans serveur, sans base ni authentification.')
    parser.add_argument('--matrix', action='store_true', help='Lot 2 : collecter les pages des deux thèmes sans arrêter au premier défaut.')
    parser.add_argument('--presentation', action='store_true', help='Avec --matrix : contrastes rendus et documents d’impression HTML (lot 3).')
    parser.add_argument('--accessibility', action='store_true', help='Connexion, réinitialisation et rendus isolés des templates d’erreur.')
    parser.add_argument('--server', choices=['single', 'threaded'], default='threaded', help='Comparatif serveur ; single conserve le mode mono-thread antérieur.')
    parser.add_argument('--lot1-case', choices=['all', 'dashboard-360-sans-js-mouse'], default='all')
    parser.add_argument('--lot1-repeat', type=int, choices=range(1, 21), default=1)
    parser.add_argument('--role', choices=['all', 'administrateur', 'pharmacien', 'caissier', 'stock', 'gestion'], default='all')
    parser.add_argument('--output', type=Path, help='Dossier de résultats neuf ; sinon dossier temporaire conservé.')
    args = parser.parse_args()
    if args.presentation and not args.matrix:
        parser.error('--presentation exige --matrix (mêmes données isolées).')
    if sum([args.diagnose_lot1, args.prepare_only, args.matrix, args.probe_browser, args.accessibility]) > 1:
        parser.error('Les modes --diagnose-lot1, --matrix, --accessibility, --probe-browser et --prepare-only sont exclusifs.')
    if args.diagnose_lot1 or args.accessibility:
        args.role = 'administrateur'
    # Vérifier les outils avant toute préparation coûteuse, hors mode serveur seul.
    module = None
    if not args.prepare_only:
        if not shutil.which('node'):
            parser.error('Node est nécessaire à la recette navigateur.')
        module = playwright_module()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        output = args.output.resolve()
    else:
        output = Path(tempfile.mkdtemp(prefix='pharmagest-ux-report-'))
    if args.probe_browser:
        env = os.environ.copy()
        env.update(PLAYWRIGHT_MODULE_PATH=module, UX_OUTPUT_DIR=str(output))
        # Aucune préparation Django ni ouverture de socket de serveur dans ce mode.
        for key in ['PHARMAGEST_USERNAME', 'PHARMAGEST_PASSWORD', 'DEMO_PASSWORD']:
            env.pop(key, None)
        if 'CHROME_PATH' not in env and shutil.which('google-chrome'):
            env['CHROME_PATH'] = shutil.which('google-chrome')
        try:
            result = subprocess.run(['node', str(ROOT / 'tools/ux_browser_probe.cjs')], cwd=ROOT, env=env, timeout=90)
        finally:
            print('Résultats : ' + str(output))
        if result.returncode:
            raise RuntimeError('Échec du témoin navigateur ; voir browser-probe.json')
        return
    revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    report = {'mode': 'accessibility' if args.accessibility else 'preparation' if args.prepare_only else 'lot1-diagnostic' if args.diagnose_lot1 else 'matrix' if args.matrix else 'browser', 'status': 'running',
              'server': args.server, 'revision': revision, 'manual_visual_review': 'pending', 'roles': []}
    journal = RequestJournal(output / 'requests.jsonl') if not args.prepare_only else None
    try:
        with tempfile.TemporaryDirectory(prefix='pharmagest-ux-data-') as directory:
            password = secrets.token_urlsafe(32)
            cases = prepare(Path(directory).resolve(), password)
            if args.accessibility:
                # Rendus isolés : aucun handler HTTP ni erreur applicative provoquée.
                from django.template.loader import render_to_string
                from django.test import RequestFactory
                from django.contrib.auth.models import AnonymousUser
                request = RequestFactory().get('/')
                request.user = AnonymousUser()
                for code in [403, 404, 500]:
                    (Path(directory) / f'{code}.html').write_text(render_to_string(f'{code}.html', request=request))
            cases = [case for case in cases if args.role in ['all', case['role']]]
            if args.prepare_only:
                report.update(status='preparation_ok', roles=[dict(role=c['role'], rendered=c['rendered']) for c in cases])
                print('Données fictives et rendus serveur vérifiés. Aucun contrôle navigateur exécuté.')
            else:
                from django.contrib.staticfiles.handlers import StaticFilesHandler
                from django.core.wsgi import get_wsgi_application
                with create_server(StaticFilesHandler(get_wsgi_application()), args.server, journal) as server:
                    thread = threading.Thread(target=server.serve_forever, daemon=True)
                    thread.start()
                    failures = []
                    try:
                        for case in cases:
                            print('Recette navigateur : ' + case['role'], flush=True)
                            env = os.environ.copy()
                            # Éviter d'hériter d'une recette dirigée vers la base active.
                            for key in ['UX_ROUTES', 'UX_WIZARD', 'PHARMAGEST_SALE_ID', 'UX_LOT1_CASE', 'UX_LOT1_REPEAT', 'UX_PRESENTATION']:
                                env.pop(key, None)
                            env['UX_PRESENTATION'] = '1' if args.presentation else '0'
                            if args.accessibility:
                                env['UX_ERROR_FIXTURES'] = directory
                            env.update(UX_ROLE=case['role'], PLAYWRIGHT_MODULE_PATH=module, PHARMAGEST_URL=f'http://127.0.0.1:{server.server_port}',
                                       PHARMAGEST_USERNAME=case['username'], PHARMAGEST_PASSWORD=password,
                                       UX_ROUTES=','.join(case['routes']), UX_OUTPUT_DIR=str(output / case['role']),
                                       UX_WIZARD='1' if case['wizard'] else '0')
                            if args.diagnose_lot1:
                                env.update(UX_LOT1_CASE=args.lot1_case, UX_LOT1_REPEAT=str(args.lot1_repeat))
                            if case['sale_id']:
                                env['PHARMAGEST_SALE_ID'] = str(case['sale_id'])
                            if 'CHROME_PATH' not in env and shutil.which('google-chrome'):
                                env['CHROME_PATH'] = shutil.which('google-chrome')
                            script = 'ux_accessibility.cjs' if args.accessibility else 'ux_lot1_diagnose.cjs' if args.diagnose_lot1 else 'ux_matrix_check.cjs' if args.matrix else 'ux_browser_check.cjs'
                            try:
                                result = subprocess.run(['node', str(ROOT / 'tools' / script)], cwd=ROOT, env=env,
                                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=600)
                            except subprocess.TimeoutExpired:
                                if not args.matrix:
                                    raise
                                failures.append(case['role'])
                                report['roles'].append(dict(role=case['role'], status='timeout'))
                                (output / (case['role'] + '.log')).write_text('Délai maximal de 600 s atteint ; consulter matrix.json pour les résultats partiels et les cas non exécutés.\n')
                                continue
                            (output / (case['role'] + '.log')).write_text(result.stdout.replace(password, '[masqué]'))
                            report['roles'].append(dict(role=case['role'], status='ok' if result.returncode == 0 else 'failed'))
                            if result.returncode:
                                if args.matrix:
                                    print('Défauts collectés pour ' + case['role'] + ' ; voir son journal et matrix.json.', flush=True)
                                else:
                                    print(result.stdout.replace(password, '[masqué]'), flush=True)
                                failures.append(case['role'])
                                if not args.matrix:
                                    raise RuntimeError('Échec navigateur pour ' + case['role'] + '. Consulter le journal dans ' + str(output))
                    finally:
                        journal.record('cleanup_started')
                        server.close_clients()
                        server.shutdown()
                        thread.join(timeout=5)
                if failures:
                    raise RuntimeError('Recette terminée avec échecs : ' + ', '.join(failures) + '. Voir ' + str(output))
                report['status'] = 'automated_checks_ok_manual_review_pending' if (args.matrix or args.accessibility) else 'automated_checks_ok'
                if args.matrix:
                    report['deferred'] = ['Filtre de période validé séparément : rapport dbxll7ue, 20/20 ; non réexercé dans la matrice', 'Examen visuel, ordre complet du clavier et parcours métier à compléter']
    except Exception as error:
        report.update(status='failed', error=str(error))
        raise
    finally:
        report['presentation_requested'] = args.presentation
        if args.diagnose_lot1:
            diagnostic = output / 'administrateur/lot1.json'
            trials = json.loads(diagnostic.read_text()) if diagnostic.exists() else []
            report['trials'] = dict(requested=args.lot1_repeat * (12 if args.lot1_case == 'all' else 1), executed=len(trials), ok=sum(row['status'] == 'OK' for row in trials), ko=sum(row['status'] == 'KO' for row in trials))
        if journal is not None:
            report['http'] = journal.summary()
            print('Requêtes HTTP reçues : ' + str(report['http']['requests_received']))
        (output / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print('Résultats : ' + str(output))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
