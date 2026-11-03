#!/usr/bin/env python3
"""Quinze ventes Playwright, exclusivement sur base et médias temporaires."""
import argparse
from datetime import timedelta
import json
import os
from pathlib import Path
import platform
import secrets
import shutil
import subprocess
import tempfile
import threading
from run_ux_review import ROOT, prepare, playwright_module
from ux_review_server import RequestJournal, create_server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resubmission", action="store_true", help="Double clic, Entrée répétée, retour navigateur ; douze ventes isolées.")
    args = parser.parse_args()
    module = playwright_module()
    output = Path(tempfile.mkdtemp(prefix='pharmagest-cashier-report-'))
    report = {'mode':'resubmission' if args.resubmission else 'timing', 'status': 'non exécuté', 'machine': platform.platform(), 'latency': 'localhost, sans limitation réseau artificielle', 'browser_result': 'non exécuté'}
    try:
        with tempfile.TemporaryDirectory(prefix='pharmagest-cashier-data-') as directory:
            password = secrets.token_urlsafe(32)
            prepare(Path(directory), password)
            from django.contrib.auth.models import User
            from django.contrib.staticfiles.handlers import StaticFilesHandler
            from django.core.wsgi import get_wsgi_application
            from django.utils import timezone
            from pharmacy.models import Medicine, Lot, Sale, Category, Payment, StockMovement
            user = User.objects.get(username='ux_caissier')
            products = []
            for i in range(3):
                med = Medicine.objects.create(name=f'Produit fictif chrono {i+1}', category=Category.objects.first(), form='Comprimé', barcode=f'UXCHRONO{i}', purchase_price='1000', sale_price='1500', authorized=True, requires_prescription=i==2)
                lot = Lot.objects.create(medicine=med, number=f'CHRONO-{i}', expires_on=timezone.localdate()+timedelta(days=30 if i==1 else 365), quantity=100, received_quantity=100, unit_cost='1000')
                products.append({'id':med.pk,'barcode':med.barcode,'lot':lot.pk,'prescription':i==2})
            trials = []
            if args.resubmission:
                for scenario in ['double-clic', 'entree-repetee', 'retour']:
                    for javascript in [True, False]:
                        for width in [360, 1280]:
                            sale = Sale.objects.create(author=user)
                            trials.append({'scenario':scenario, 'javascript':javascript, 'width':width, 'sale':sale.pk, 'products':[products[0]]})
            else:
                for scenario, indices in [('simple',[0]),('trois-produits',[0,1,2]),('ordonnance',[2])]:
                    for iteration in range(1,6):
                        sale = Sale.objects.create(author=user)
                        trials.append({'scenario':scenario,'iteration':iteration,'sale':sale.pk,'products':[products[i] for i in indices]})
            journal = RequestJournal(output/'requests.jsonl')
            with create_server(StaticFilesHandler(get_wsgi_application()),'threaded',journal) as server:
                thread = threading.Thread(target=server.serve_forever,daemon=True);thread.start()
                try:
                    env=os.environ.copy()
                    env.update(PLAYWRIGHT_MODULE_PATH=module, PHARMAGEST_URL=f'http://127.0.0.1:{server.server_port}', PHARMAGEST_USERNAME=user.username,PHARMAGEST_PASSWORD=password,UX_OUTPUT_DIR=str(output),UX_BENCH_TRIALS=json.dumps(trials))
                    if 'CHROME_PATH' not in env and shutil.which('google-chrome'):env['CHROME_PATH']=shutil.which('google-chrome')
                    run=subprocess.run(['node',str(ROOT/('tools/ux_cashier_resubmission.cjs' if args.resubmission else 'tools/ux_cashier_benchmark.cjs'))],env=env,cwd=ROOT,capture_output=True,text=True,timeout=600)
                    (output/'browser.log').write_text(run.stdout.replace(password,'[masqué]')+run.stderr.replace(password,'[masqué]'))
                    report['browser_result']='OK' if run.returncode==0 else 'KO'
                    audits=[]
                    for trial in trials:
                        sale=Sale.objects.get(pk=trial['sale'])
                        audits.append({'sale':sale.pk,'status':sale.status,'payments':Payment.objects.filter(sale=sale).count(),'sale_movements':StockMovement.objects.filter(sale=sale,kind='sale').count(),'stock_delta':sum(StockMovement.objects.filter(sale=sale,kind='sale').values_list('quantity',flat=True)),'lines':sale.lines.count(),'quantity':sum(line.quantity for line in sale.lines.all())})
                    integrity = all(a['status'] == 'validated' and a['payments'] == 1 and a['quantity'] == len(t['products']) and a['sale_movements'] == len(t['products']) and a['stock_delta'] == -len(t['products']) for a,t in zip(audits,trials))
                    stocks = []
                    for product in products:
                        sold = sum(t['products'].count(product) for t in trials if Sale.objects.get(pk=t['sale']).status == 'validated')
                        remaining = Lot.objects.get(pk=product['lot']).quantity
                        stocks.append({'lot':product['lot'], 'expected':100-sold, 'actual':remaining})
                    integrity = integrity and all(s['expected'] == s['actual'] for s in stocks)
                    report.update(status='exécuté',audits=audits,stocks=stocks,integrity=integrity,http=journal.summary())
                    if not integrity: report['browser_result']='KO'
                    if run.returncode:print('Défauts : consulter browser.log et ' + ('resubmission.json' if args.resubmission else 'timings.json'))
                finally:
                    server.close_clients();server.shutdown();thread.join(timeout=5)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        report['error']=str(exc)
        if isinstance(exc, subprocess.TimeoutExpired):
            report.update(status='interrompu', browser_result='timeout')
            partial = exc.stdout or b''
            if isinstance(partial, bytes): partial = partial.decode(errors='replace')
            (output/'browser.log').write_text(partial.replace(password, '[masqué]'))
    finally:
        (output/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print('Résultats : '+str(output))
    return 0 if report['browser_result']=='OK' else 1


if __name__=='__main__':
    raise SystemExit(main())
