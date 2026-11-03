#!/usr/bin/env python3
"""Génère les PDF réels et des tableaux longs sur une base fictive temporaire."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile
from run_ux_review import prepare


def main():
    try:
        import reportlab
    except ImportError:
        print('ReportLab absent : installer requirements.txt dans un environnement de recette propre. Aucun PDF ReportLab vérifié.')
        return 1
    missing = [tool for tool in ['pdftotext', 'pdftoppm', 'pdfinfo'] if not shutil.which(tool)]
    if missing:
        print('Outils PDF manquants : ' + ', '.join(missing))
        return 1
    output = Path(tempfile.mkdtemp(prefix='pharmagest-pdf-report-'))
    report = {'reportlab':reportlab.Version,'status':'en cours','documents':[], 'visual_review':'non exécuté, images à examiner'}
    try:
        with tempfile.TemporaryDirectory(prefix='pharmagest-pdf-data-') as directory:
            prepare(Path(directory), secrets.token_urlsafe(32))
            from django.contrib.auth.models import User
            from django.test import Client
            from pharmacy.models import Sale, Purchase, Receipt
            from pharmacy.pdf import document_response
            client = Client();client.force_login(User.objects.get(username='ux_administrateur'))
            sale=Sale.objects.filter(status='validated').first()
            purchase=Purchase.objects.first();receipt=Receipt.objects.first()
            assert sale and purchase and receipt, 'Documents fictifs requis'
            routes=[('recu',f'/documents/sale/{sale.pk}.pdf',str(sale)),('facture',f'/documents/invoice/{sale.pk}.pdf',str(sale)),('commande',f'/documents/purchase/{purchase.pk}.pdf',str(purchase)),('reception',f'/documents/receipt/{receipt.pk}.pdf',str(receipt))]
            routes += [(kind,f'/rapports/{kind}.pdf',None) for kind in ['stock','expiry','sales','purchases']]
            def inspect(name,response,expected=(),multipage=False):
                item={'name':name,'result':'en cours','multipage_fixture':multipage,'expected_text':list(expected)}
                report['documents'].append(item)
                try:
                    assert response.status_code==200, f'HTTP {response.status_code}'
                    data=b''.join(response.streaming_content)
                    response.close()
                    assert data.startswith(b'%PDF-'), 'Signature PDF absente'
                    pdf=output/(name+'.pdf');pdf.write_bytes(data)
                    info=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,check=True).stdout
                    pages=int(next(line.split(':',1)[1] for line in info.splitlines() if line.startswith('Pages:')))
                    item.update(pages=pages,pdf=pdf.name,sha256=hashlib.sha256(data).hexdigest())
                    text=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,text=True,check=True).stdout
                    (output/(name+'.txt')).write_text(text)
                    for fragment in expected:assert fragment in text, f'Texte essentiel absent : {fragment}'
                    if multipage:assert pages>1,'Plusieurs pages attendues'
                    subprocess.run(['pdftoppm','-png','-r','100',str(pdf),str(output/name)],capture_output=True,check=True)
                    item['images']=[p.name for p in sorted(output.glob(name+'-*.png'))]
                    assert len(item['images'])==pages,'Nombre de pages converties incohérent'
                    item['result']='OK technique, inspection visuelle en attente'
                except Exception as exc:
                    item.update(result='KO',error=str(exc))
            for name,url,reference in routes:
                inspect(name,client.get(url),(reference,) if reference else ())
            # Stress de présentation : même moteur, sans prétendre à des ventes réelles.
            fixtures=[('long-stock',['Médicament','Lot','Péremption','Stock','État']),('long-vente',['Médicament','Lot','Qté','P.U. (Ar)','Total (Ar)']),('long-achat',['Médicament','Qté','Reçu','P.U. (Ar)','Total (Ar)'])]
            for name,headers in fixtures:
                rows=[]
                for i in range(1,81):
                    label=f'Produit fictif {i:03d} — dénomination longue, péremption, é à ç'
                    rows.append([label,f'LOT-{i:03d}','03/11/2027',i,'Disponible'] if name=='long-stock' else [label,f'LOT-{i:03d}' if name=='long-vente' else 1,1,Decimal('15000'),Decimal('15000')])
                response=document_response('Contrôle multipage '+name,headers,rows,total=None if name=='long-stock' else Decimal('1200000'),meta=['Données entièrement fictives, présentation uniquement'])
                inspect(name,response,('Produit fictif 001','Produit fictif 080'),True)
        report['status']='KO' if any(d['result']=='KO' for d in report['documents']) else 'contrôles techniques OK, inspection visuelle en attente'
    except Exception as exc:
        report.update(status='interrompu',error=str(exc))
    finally:
        (output/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print('Résultats : '+str(output))
    return 0 if report['status'].startswith('contrôles techniques OK') else 1


if __name__=='__main__':
    raise SystemExit(main())
