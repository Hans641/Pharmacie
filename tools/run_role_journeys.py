#!/usr/bin/env python3
"""Parcours HTTP réels via Client Django/CSRF, sur base temporaire (pas de navigateur)."""
from datetime import timedelta
import json
import logging
import traceback
import importlib.util
from pathlib import Path
import secrets
import tempfile
from run_ux_review import prepare


def main():
    output=Path(tempfile.mkdtemp(prefix='pharmagest-role-report-'))
    report={'scope':'Client Django avec CSRF ; JavaScript et géométrie non exécutés','pdf_engine':'ReportLab' if importlib.util.find_spec('reportlab') else 'secours texte', 'cases':[],'status':'en cours'}
    def save(): (output/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    save()
    try:
        with tempfile.TemporaryDirectory(prefix='pharmagest-role-data-') as directory:
            password=secrets.token_urlsafe(32);prepare(Path(directory),password)
            from django.contrib.auth.models import User, Group
            from django.test import Client
            from django.test.utils import setup_test_environment, teardown_test_environment
            from django.utils import timezone
            from pharmacy.models import Sale, Medicine, Lot, Purchase, Receipt, Payment, StockMovement, SaleReturn, AuditLog
            setup_test_environment()
            logging.getLogger('django.request').disabled=True
            def client(role):
                c=Client(enforce_csrf_checks=True);c.get('/comptes/login/')
                r=c.post('/comptes/login/',{'username':'ux_'+role,'password':password},HTTP_X_CSRFTOKEN=c.cookies['csrftoken'].value)
                assert r.status_code==302,'Connexion fictive refusée'
                return c
            clients={role:client(role) for role in ['administrateur','pharmacien','caissier','stock','gestion']}
            def post(c,url,data):
                c.get(url)
                return c.post(url,data,HTTP_X_CSRFTOKEN=c.cookies['csrftoken'].value)
            def case(role,name,fn):
                row={'role':role,'journey':name,'result':'en cours'};report['cases'].append(row);save()
                try: fn();row['result']='OK HTTP/état base'
                except Exception as exc:
                    frame=traceback.extract_tb(exc.__traceback__)[-1]
                    row.update(result='KO',error=str(exc) or 'Assertion échouée',location=f'{Path(frame.filename).name}:{frame.lineno}')
                save()
            med=Medicine.objects.get(barcode='9900000000000')
            def create_sale(role):
                c=clients[role];r=post(c,'/ventes/nouvelle/',{'customer':''});assert r.status_code==302
                sale=Sale.objects.get(pk=int(r['Location'].strip('/').split('/')[-1]))
                assert sale.author.username=='ux_'+role and sale.customer_id is None
                url=f'/ventes/{sale.pk}/'
                r=post(c,url,{'action':'add','medicine':med.pk,'quantity':1,'lot':''});assert r.status_code==302
                return sale,url
            def cashier():
                c=clients['caissier'];sale,url=create_sale('caissier');line=sale.lines.get();stock=Lot.objects.get(pk=line.lot_id).quantity
                r=post(c,url,{'action':'validate','method':'cash','confirm':'on'})
                sale.refresh_from_db();assert r.status_code==200 and sale.status=='draft'
                assert not Payment.objects.filter(sale=sale).exists() and Lot.objects.get(pk=line.lot_id).quantity==stock
                r=post(c,url,{'action':'validate','method':'cash','prescription_checked':'on','confirm':'on'});assert r.status_code==302
                sale.refresh_from_db();assert sale.status=='validated' and Payment.objects.filter(sale=sale).count()==1
                assert Lot.objects.get(pk=line.lot_id).quantity==stock-1
                html=c.get(url).content.decode();assert 'Ouvrir une vente comptoir' in html and f'/documents/sale/{sale.pk}.pdf' in html
                assert f'/ventes/{sale.pk}/retour/' not in html
            case('caissier','Brouillon comptoir → ajout FEFO → refus ordonnance absente → encaissement → reçu/nouvelle vente',cashier)
            def pharmacist():
                c=clients['pharmacien'];sale,url=create_sale('pharmacien')
                assert post(c,url,{'action':'validate','method':'cash','prescription_checked':'on','confirm':'on'}).status_code==302
                line=sale.lines.get();stock=Lot.objects.get(pk=line.lot_id).quantity;route=url+'retour/'
                r=c.get(route);assert r.status_code==200
                data={'line':line.pk,'quantity':1,'reason':'Retour fictif de recette','restock':'on','refund_reference':'FICTIF-RETOUR-ROLE','token':r.context['form']['token'].value(),'confirm':'on'}
                assert post(c,route,data).status_code==302
                line.refresh_from_db();assert line.returned==1 and Lot.objects.get(pk=line.lot_id).quantity==stock+1
                assert SaleReturn.objects.filter(sale=sale).count()==1 and Payment.objects.filter(sale=sale).count()==1
                assert 'Retours et remboursements' in c.get(url).content.decode()
            case('pharmacien','Délivrance avec ordonnance → retour fictif référencé → remise en stock',pharmacist)
            def stock():
                c=clients['stock'];purchase=Purchase.objects.get(status='partial');line=purchase.lines.first();received=line.received;route=f'/achats/{purchase.pk}/reception/'
                r=c.get(route);data={'line':line.pk,'quantity':1,'number':'ROLE-RECEPTION','expires_on':str(timezone.localdate()+timedelta(days=365)),'token':r.context['form']['token'].value(),'confirm':'on'}
                assert post(c,route,data).status_code==302
                line.refresh_from_db();purchase.refresh_from_db();assert line.received==received+1 and purchase.status=='partial'
                lot=Lot.objects.get(number='ROLE-RECEPTION');assert lot.quantity==1
                route=f'/stocks/{lot.pk}/inventaire/'
                assert post(c,route,{'counted':1,'reason':'Blocage fictif de recette','blocked':'on','confirm':'on'}).status_code==302
                lot.refresh_from_db();assert lot.blocked and lot.quantity==1
                assert StockMovement.objects.filter(lot=lot,kind='inventory').exists(), 'Mouvement inventaire absent'
            case('stock','Réception partielle → stock augmenté → inventaire et blocage tracés',stock)
            def gestion():
                c=clients['gestion']
                for url in ['/rapports/','/audit/','/mouvements/']:
                    assert c.get(url).status_code==200,url
                for kind in ['sales','purchases','stock','expiry']:
                    r=c.get(f'/rapports/{kind}.pdf');assert r.status_code==200 and r['Content-Type']=='application/pdf'
                    assert b''.join(r.streaming_content).startswith(b'%PDF-');r.close()
            case('gestion','Consultation rapports/audit/mouvements → quatre exports PDF',gestion)
            def admin():
                c=clients['administrateur'];group=Group.objects.get(name='Caissier')
                data={'username':'recette_compte_fictif','first_name':'Compte fictif','last_name':'Recette','email':'','password1':password,'password2':password,'groups':[group.pk],'is_active':'on'}
                r=post(c,'/utilisateurs/ajouter/',data);assert r.status_code==302,'Création du compte fictif refusée'
                user=User.objects.get(username='recette_compte_fictif');assert user.is_active and user.groups.filter(pk=group.pk).exists() and not user.is_superuser
                assert c.get('/audit/').status_code==200 and AuditLog.objects.filter(action__contains='compte').exists()
            case('administrateur','Création utilisateur fictif avec rôle → journal d’audit',admin)
            sale=Sale.objects.filter(status='validated').first();lot=Lot.objects.first();purchase=Purchase.objects.first()
            forbidden={'caissier':[f'/ventes/{sale.pk}/retour/',f'/stocks/{lot.pk}/inventaire/','/utilisateurs/ajouter/'], 'stock':[f'/ventes/{sale.pk}/','/utilisateurs/ajouter/'], 'gestion':['/ventes/nouvelle/',f'/stocks/{lot.pk}/inventaire/',f'/achats/{purchase.pk}/reception/'], 'pharmacien':['/utilisateurs/ajouter/']}
            def snapshot(): return (Sale.objects.count(),Payment.objects.count(),SaleReturn.objects.count(),StockMovement.objects.count(),list(Lot.objects.order_by('pk').values_list('pk','quantity','blocked')),User.objects.count())
            for role,urls in forbidden.items():
                for url in urls:
                    def denied(role=role,url=url):
                        c=clients[role];before=snapshot();assert c.get(url).status_code==403
                        assert post(c,url,{'confirm':'on'}).status_code==403
                        assert snapshot()==before,'Mutation après accès interdit'
                    case(role,'Refus GET/POST sans mutation : '+url,denied)
            def csrf():
                c=clients['caissier'];before=snapshot()
                assert c.post('/ventes/nouvelle/',{'customer':''}).status_code==403
                assert snapshot()==before
            case('caissier','Refus POST sans CSRF, sans création de vente',csrf)
            teardown_test_environment()
        report['status']='KO' if any(r['result']=='KO' for r in report['cases']) else 'OK serveur ; recette humaine/navigateur restante'
    except Exception as exc:report.update(status='interrompu',error=str(exc))
    finally:save();print('Résultats : '+str(output))
    for row in report['cases']:print(row['result'],row['role'],row['journey'],row.get('error',''))
    return 0 if report['status'].startswith('OK serveur') else 1


if __name__=='__main__':
    raise SystemExit(main())
