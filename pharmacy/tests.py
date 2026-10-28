import tempfile, uuid, threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from io import BytesIO, StringIO
from pathlib import Path
from PIL import Image
from django.contrib.auth.models import User,Group
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection, connections, close_old_connections, OperationalError, transaction
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from .models import *
from . import services,forms
from .management.commands.setup_roles import setup_roles

class Fixtures:
    def make_data(self):
        self.user=User.objects.create_superuser('admin','admin@example.test','A-long-test-password42!')
        self.other=User.objects.create_user('other',password='A-long-test-password42!')
        self.category=Category.objects.create(name='Antalgiques')
        self.med=Medicine.objects.create(name='Produit test',category=self.category,form='Comprimé',purchase_price=Decimal('10'),sale_price=Decimal('20'),authorized=True)
        self.supplier=Supplier.objects.create(name='Fournisseur test',phone='0340000000')
    def purchase(self,quantity=20):
        p=Purchase.objects.create(supplier=self.supplier,author=self.user)
        line=services.add_purchase_line(self.user,p.pk,self.med,quantity,Decimal('10'))
        return p,line
    def received(self,quantity=20,days=100,number='LOT-001'):
        p,line=self.purchase(quantity);services.order_purchase(self.user,p.pk)
        receipt=services.receive_purchase(self.user,p.pk,[{'line_id':line.pk,'quantity':quantity,'number':number,'expires_on':timezone.localdate()+timedelta(days=days)}],uuid.uuid4())
        return receipt.lines.get().lot
    def sale(self,quantity=3):
        sale=Sale.objects.create(author=self.user)
        services.add_sale_line(self.user,sale.pk,self.med,quantity)
        return sale

class BusinessTests(Fixtures,TestCase):
    def setUp(self):self.make_data()
    def test_order_does_not_change_stock(self):
        p,line=self.purchase();services.order_purchase(self.user,p.pk)
        self.assertEqual(self.med.available,0);self.assertFalse(StockMovement.objects.exists())
    def test_receipt_increases_only_once(self):
        p,line=self.purchase();services.order_purchase(self.user,p.pk);token=uuid.uuid4()
        items=[{'line_id':line.pk,'quantity':20,'number':'ONE','expires_on':timezone.localdate()+timedelta(days=100)}]
        a=services.receive_purchase(self.user,p.pk,items,token);b=services.receive_purchase(self.user,p.pk,items,token)
        self.assertEqual(a.pk,b.pk);self.assertEqual(self.med.available,20)
        self.assertEqual(StockMovement.objects.count(),1);p.refresh_from_db();self.assertEqual(p.status,'received')
    def test_partial_receipt(self):
        p,line=self.purchase();services.order_purchase(self.user,p.pk)
        services.receive_purchase(self.user,p.pk,[{'line_id':line.pk,'quantity':8,'number':'PART','expires_on':timezone.localdate()+timedelta(days=50)}],uuid.uuid4())
        p.refresh_from_db();line.refresh_from_db()
        self.assertEqual(p.status,'partial');self.assertEqual(line.remaining,12);self.assertEqual(self.med.available,8)
    def test_excess_receipt_rolls_back(self):
        p,line=self.purchase();services.order_purchase(self.user,p.pk)
        with self.assertRaises(ValidationError):services.receive_purchase(self.user,p.pk,[{'line_id':line.pk,'quantity':21,'number':'NO','expires_on':timezone.localdate()+timedelta(days=50)}],uuid.uuid4())
        self.assertFalse(Receipt.objects.exists());self.assertFalse(Lot.objects.exists());self.assertFalse(StockMovement.objects.exists())
    def test_expired_receipt_rejected(self):
        p,line=self.purchase();services.order_purchase(self.user,p.pk)
        with self.assertRaises(ValidationError):services.receive_purchase(self.user,p.pk,[{'line_id':line.pk,'quantity':1,'number':'NO','expires_on':timezone.localdate()-timedelta(days=1)}],uuid.uuid4())
        self.assertEqual(self.med.available,0)
    def test_received_purchase_cannot_be_cancelled(self):
        self.received();p=Purchase.objects.first()
        with self.assertRaises(ValidationError):services.order_purchase(self.user,p.pk,cancel=True)
    def test_sale_deducts_only_once(self):
        lot=self.received();sale=self.sale()
        self.assertEqual(self.med.available,20)
        services.validate_sale(self.user,sale.pk);services.validate_sale(self.user,sale.pk)
        lot.refresh_from_db();self.assertEqual(lot.quantity,17)
        self.assertEqual(Payment.objects.count(),1);self.assertEqual(StockMovement.objects.filter(kind='sale').count(),1)
    def test_fefo_splits_across_lots(self):
        later=self.received(10,100,'LATER');earlier=self.received(2,20,'EARLIER')
        sale=self.sale(4);lines=list(sale.lines.order_by('pk'))
        self.assertEqual([(l.lot_id,l.quantity) for l in lines],[(earlier.pk,2),(later.pk,2)])
    def test_specific_lot_respected(self):
        a=self.received(10,100,'A');b=self.received(10,20,'B');sale=Sale.objects.create(author=self.user)
        services.add_sale_line(self.user,sale.pk,self.med,2,lot_id=a.pk)
        self.assertEqual(sale.lines.get().lot_id,a.pk)
    def test_overstock_add_rolls_back(self):
        self.received(2)
        with self.assertRaises(ValidationError):self.sale(3)
        self.assertFalse(SaleLine.objects.exists())
    def test_zero_negative_noninteger_refused(self):
        self.received()
        sale=Sale.objects.create(author=self.user)
        for n in [0,-1,1.5,True]:
            with self.assertRaises(ValidationError):services.add_sale_line(self.user,sale.pk,self.med,n)
        self.assertFalse(sale.lines.exists())
    def test_stock_rechecked_at_validation_and_atomic(self):
        lot=self.received(3);a=self.sale(2);b=self.sale(2)
        services.validate_sale(self.user,a.pk)
        with self.assertRaises(ValidationError):services.validate_sale(self.user,b.pk)
        b.refresh_from_db();lot.refresh_from_db();self.assertEqual(b.status,'draft');self.assertEqual(lot.quantity,1)
        self.assertFalse(Payment.objects.filter(sale=b).exists())
    def test_multiline_sale_rollback_on_later_failure(self):
        a=self.received(2,20,'A');b=self.received(2,50,'B');sale=self.sale(4)
        Lot.objects.filter(pk=b.pk).update(blocked=True)
        with self.assertRaises(ValidationError):services.validate_sale(self.user,sale.pk)
        a.refresh_from_db();self.assertEqual(a.quantity,2);self.assertFalse(StockMovement.objects.filter(kind='sale').exists())
    def test_expired_and_blocked_lots_refused(self):
        lot=self.received();sale=self.sale()
        for values in [{'blocked':True},{'blocked':False,'expires_on':timezone.localdate()-timedelta(days=1)}]:
            Lot.objects.filter(pk=lot.pk).update(**values)
            with self.assertRaises(ValidationError):services.validate_sale(self.user,sale.pk)
        self.assertFalse(Payment.objects.exists())
    def test_unauthorized_medicine_refused(self):
        self.received();self.med.authorized=False;self.med.save()
        with self.assertRaises(ValidationError):self.sale()
    def test_prescription_control_required(self):
        self.received();self.med.requires_prescription=True;self.med.save();sale=self.sale()
        with self.assertRaises(ValidationError):services.validate_sale(self.user,sale.pk)
        services.validate_sale(self.user,sale.pk,prescription_checked=True)
        sale.refresh_from_db();self.assertTrue(sale.prescription_checked)
    def test_historical_prices_unchanged(self):
        self.received();sale=self.sale();services.validate_sale(self.user,sale.pk)
        self.med.sale_price=Decimal('100');self.med.save()
        self.assertEqual(sale.total,Decimal('60'));self.assertEqual(sale.payment.amount,Decimal('60'))
    def test_electronic_payment_requires_verification(self):
        self.received();sale=self.sale()
        with self.assertRaises(ValidationError):services.validate_sale(self.user,sale.pk,method='mobile')
        self.assertEqual(self.med.available,20)
        services.validate_sale(self.user,sale.pk,method='mobile',reference='PROVIDER-VERIFIED-01',verified=True)
        self.assertTrue(sale.payment.confirmed)
    def test_cashier_cannot_verify_mobile(self):
        setup_roles();self.other.groups.add(Group.objects.get(name='Caissier'));self.received();sale=self.sale()
        with self.assertRaises(PermissionDenied):services.validate_sale(self.other,sale.pk,method='mobile',reference='X',verified=True)
    def test_return_idempotent_and_original_kept(self):
        lot=self.received();sale=self.sale();services.validate_sale(self.user,sale.pk);line=sale.lines.get();token=uuid.uuid4()
        a=services.return_sale(self.user,line.pk,2,'Erreur de délivrance',True,'REM-1',token)
        b=services.return_sale(self.user,line.pk,2,'Erreur de délivrance',True,'REM-1',token)
        lot.refresh_from_db();line.refresh_from_db()
        self.assertEqual(a.pk,b.pk);self.assertEqual(lot.quantity,19);self.assertEqual(line.returned,2)
        self.assertEqual(sale.total,Decimal('60'));self.assertEqual(sale.refunded,Decimal('40'))
    def test_return_without_restock(self):
        lot=self.received();sale=self.sale();services.validate_sale(self.user,sale.pk)
        services.return_sale(self.user,sale.lines.get().pk,1,'Emballage ouvert',False,'REM-2',uuid.uuid4())
        lot.refresh_from_db();self.assertEqual(lot.quantity,17)
    def test_excess_return_and_expired_restock_refused(self):
        lot=self.received();sale=self.sale();services.validate_sale(self.user,sale.pk);line=sale.lines.get()
        with self.assertRaises(ValidationError):services.return_sale(self.user,line.pk,4,'Motif',True,'REF',uuid.uuid4())
        Lot.objects.filter(pk=lot.pk).update(expires_on=timezone.localdate()-timedelta(days=1))
        with self.assertRaises(ValidationError):services.return_sale(self.user,line.pk,1,'Motif',True,'REF',uuid.uuid4())
        self.assertFalse(SaleReturn.objects.exists())
    def test_inventory_trace_and_no_negative(self):
        lot=self.received();services.adjust_stock(self.user,lot.pk,18,'Comptage physique',True)
        lot.refresh_from_db();self.assertEqual(lot.quantity,18);self.assertTrue(lot.blocked)
        self.assertEqual(StockMovement.objects.first().quantity,-2)
        with self.assertRaises(ValidationError):services.adjust_stock(self.user,lot.pk,-1,'Comptage',False)
    def test_service_permissions(self):
        lot=self.received()
        with self.assertRaises(PermissionDenied):services.adjust_stock(self.other,lot.pk,1,'Test',False)
        with self.assertRaises(PermissionDenied):services.add_sale_line(self.other,Sale.objects.create(author=self.other).pk,self.med,1)
    def test_barcode_unique_and_empty_allowed(self):
        self.med.barcode='ABC';self.med.save()
        second=Medicine(name='Second',category=self.category,form='Sirop',purchase_price=1,sale_price=2,barcode='ABC')
        with self.assertRaises(ValidationError):second.full_clean()
        second.barcode='';second.full_clean();second.save();self.assertIsNone(second.barcode)
    def test_negative_prices_invalid(self):
        self.med.sale_price=-1
        with self.assertRaises(ValidationError):self.med.full_clean()

class InterfaceTests(Fixtures,TestCase):
    def setUp(self):self.make_data();self.client.force_login(self.user)
    def test_all_main_pages_render(self):
        for url in ['/','/catalogue/medicaments/','/catalogue/categories/','/catalogue/fournisseurs/','/catalogue/clients/','/achats/','/ventes/','/stocks/','/mouvements/','/audit/','/utilisateurs/','/rapports/','/comptes/password_change/']:
            with self.subTest(url=url):self.assertEqual(self.client.get(url).status_code,200)
    def test_details_and_forms_render(self):
        lot=self.received();sale=self.sale();p=Purchase.objects.first()
        for url in [f'/catalogue/medicaments/{self.med.pk}/',f'/catalogue/fournisseurs/{self.supplier.pk}/',f'/catalogue/medicaments/{self.med.pk}/modifier/','/catalogue/medicaments/ajouter/','/achats/nouveau/',f'/achats/{p.pk}/',f'/achats/{p.pk}/reception/',f'/ventes/{sale.pk}/','/ventes/nouvelle/',f'/stocks/{lot.pk}/inventaire/','/utilisateurs/ajouter/',f'/utilisateurs/{self.other.pk}/']:
            with self.subTest(url=url):self.assertEqual(self.client.get(url).status_code,200)
        services.validate_sale(self.user,sale.pk)
        self.assertEqual(self.client.get(f'/ventes/{sale.pk}/').status_code,200)
        self.assertEqual(self.client.get(f'/ventes/{sale.pk}/retour/').status_code,200)
    def test_anonymous_redirected_and_logout_post_only(self):
        self.client.logout();self.assertEqual(self.client.get('/stocks/').status_code,302)
        self.client.force_login(self.user);self.assertEqual(self.client.get('/comptes/logout/').status_code,405)
    def test_forbidden_direct_urls_and_reports(self):
        lot=self.received();self.client.force_login(self.other)
        for url in ['/catalogue/medicaments/','/catalogue/medicaments/ajouter/','/achats/','/ventes/','/stocks/','/utilisateurs/','/audit/','/rapports/sales.pdf','/rapports/stock.pdf',f'/stocks/{lot.pk}/inventaire/']:
            with self.subTest(url=url):self.assertEqual(self.client.get(url).status_code,403)
        self.assertEqual(self.client.get('/').status_code,200)
        self.assertNotContains(self.client.get('/'),'Chiffre d’affaires brut')
    def test_csrf_enforced(self):
        from django.test import Client
        client=Client(enforce_csrf_checks=True);client.force_login(self.user)
        self.assertEqual(client.post('/ventes/nouvelle/',{}).status_code,403)
    def test_photo_create_and_modify(self):
        with tempfile.TemporaryDirectory() as directory,override_settings(MEDIA_ROOT=directory):
            image=BytesIO();Image.new('RGB',(32,32),'green').save(image,format='PNG')
            photo=SimpleUploadedFile('photo.png',image.getvalue(),content_type='image/png')
            data={'name':'Avec photo','category':self.category.pk,'form':'Sirop','purchase_price':'12.50','sale_price':'25.00','threshold':'4','active':'on','authorized':'on','photo':photo}
            response=self.client.post('/catalogue/medicaments/ajouter/',data);self.assertEqual(response.status_code,302)
            med=Medicine.objects.get(name='Avec photo');self.assertTrue(Path(med.photo.path).exists())
            self.assertContains(self.client.get('/catalogue/medicaments/'),med.photo.url)
            data.pop('photo');data['name']='Photo modifiée'
            self.assertEqual(self.client.post(f'/catalogue/medicaments/{med.pk}/modifier/',data).status_code,302)
            med.refresh_from_db();self.assertEqual(med.name,'Photo modifiée')
            self.client.force_login(self.other);self.assertEqual(self.client.get(med.photo.url).status_code,403)
    def test_invalid_photo_rejected(self):
        form=forms.MedicineForm({'name':'Test','category':self.category.pk,'form':'Sirop','purchase_price':'1','sale_price':'2','threshold':'1'}, {'photo':SimpleUploadedFile('evil.png',b'not an image',content_type='image/png')})
        self.assertFalse(form.is_valid());self.assertIn('photo',form.errors)
    def test_large_photo_rejected(self):
        f=SimpleUploadedFile('large.png',b'x'*(5*1024*1024+1))
        with self.assertRaises(ValidationError):validate_photo(f)
    def test_archival_preserves_history_and_used_category(self):
        lot=self.received();sale=self.sale();services.validate_sale(self.user,sale.pk)
        self.client.post(f'/catalogue/medicaments/{self.med.pk}/archiver/')
        self.med.refresh_from_db();self.assertFalse(self.med.active);self.assertEqual(SaleLine.objects.count(),1)
        self.client.post(f'/catalogue/categories/{self.category.pk}/archiver/')
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
    def test_search_filter_pagination(self):
        response=self.client.get('/catalogue/medicaments/',{'q':'Produit','category':self.category.pk,'sort':'sale_price'})
        self.assertContains(response,'Produit test')
        self.assertNotContains(self.client.get('/catalogue/medicaments/',{'q':'inexistant'}),'Produit test')
    def test_pdf_documents_and_reports(self):
        lot=self.received();sale=self.sale();services.validate_sale(self.user,sale.pk)
        for url in [f'/documents/sale/{sale.pk}.pdf',f'/documents/invoice/{sale.pk}.pdf',f'/documents/purchase/{Purchase.objects.first().pk}.pdf',f'/documents/receipt/{Receipt.objects.first().pk}.pdf','/rapports/stock.pdf','/rapports/expiry.pdf','/rapports/sales.pdf','/rapports/purchases.pdf']:
            with self.subTest(url=url):
                response=self.client.get(url);self.assertEqual(response.status_code,200);self.assertEqual(response['Content-Type'],'application/pdf')
                data=b''.join(response.streaming_content);self.assertTrue(data.startswith(b'%PDF-'));self.assertGreater(len(data),500)
    def test_invalid_period_and_category_do_not_crash(self):
        self.assertEqual(self.client.get('/?start=bad&end=2020-01-01').status_code,200)
        self.assertEqual(self.client.get('/catalogue/medicaments/?category=bad&sort=bad').status_code,200)
    def test_cashier_barcode_search_selects_product(self):
        self.med.barcode='SCAN-123';self.med.save();sale=Sale.objects.create(author=self.user)
        response=self.client.get(f'/ventes/{sale.pk}/',{'q':'SCAN-123'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['cart'].initial['medicine'],self.med.pk)
        self.assertEqual(list(response.context['cart'].fields['medicine'].queryset),[self.med])
    def test_remove_purchase_line_only_in_draft(self):
        p,line=self.purchase()
        self.client.post(f'/achats/{p.pk}/',{'action':'remove','line':line.pk})
        self.assertFalse(p.lines.exists())
        line=services.add_purchase_line(self.user,p.pk,self.med,2,Decimal('10'))
        services.order_purchase(self.user,p.pk)
        with self.assertRaises(ValidationError):services.remove_purchase_line(self.user,p.pk,line.pk)
        self.assertTrue(p.lines.exists())
    def test_password_reset_pages(self):
        self.client.logout()
        self.assertEqual(self.client.get('/comptes/password_reset/').status_code,200)
        response=self.client.post('/comptes/password_reset/',{'email':'nobody@example.test'})
        self.assertEqual(response.status_code,302)
    def test_no_superuser_escalation_from_account_form(self):
        setup_roles();self.other.groups.add(Group.objects.get(name='Administrateur'));self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/utilisateurs/{self.user.pk}/').status_code,403)
        response=self.client.post('/utilisateurs/ajouter/',{'username':'new','password1':'Different-long-password42!','password2':'Different-long-password42!','is_superuser':'on','is_staff':'on','is_active':'on'})
        self.assertEqual(response.status_code,302)
        new=User.objects.get(username='new');self.assertFalse(new.is_superuser);self.assertFalse(new.is_staff)

class BackupTests(Fixtures,TransactionTestCase):
    def setUp(self):self.make_data()
    def test_backup_restore_preserves_records_and_private_mode(self):
        # SQLite en mémoire partagée : la commande doit utiliser la connexion Django.
        with tempfile.TemporaryDirectory() as directory:
            backup=Path(directory)/'backup.sqlite3';restored=Path(directory)/'restored.sqlite3'
            call_command('backup_db',str(backup),stdout=StringIO())
            call_command('restore_db',str(backup),str(restored),stdout=StringIO())
            import sqlite3
            with sqlite3.connect(restored) as db:
                self.assertEqual(db.execute('SELECT name FROM pharmacy_medicine').fetchone()[0],'Produit test')
            self.assertEqual(backup.stat().st_mode & 0o777,0o600)
            with self.assertRaises(CommandError):call_command('restore_db',str(backup),str(restored),stdout=StringIO())

class ConcurrentSaleTests(Fixtures,TransactionTestCase):
    def setUp(self):self.make_data()
    def run_parallel(self,sale_ids):
        barrier=threading.Barrier(2);user_id=self.user.pk
        def worker(sale_id):
            close_old_connections()
            try:
                user=User.objects.get(pk=user_id);barrier.wait(timeout=10)
                try:services.validate_sale(user,sale_id);return 'ok'
                except (ValidationError,OperationalError):return 'refused'
            finally:connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:return list(pool.map(worker,sale_ids))
    def test_same_sale_validated_concurrently_no_duplicate(self):
        lot=self.received(5);sale=self.sale(3);results=self.run_parallel([sale.pk,sale.pk])
        lot.refresh_from_db()
        # Sur SQLite mémoire, les écritures concurrentes peuvent être refusées : aucun doublon autorisé.
        if 'ok' not in results:services.validate_sale(self.user,sale.pk);lot.refresh_from_db()
        self.assertEqual(lot.quantity,2);self.assertEqual(Payment.objects.count(),1)
        self.assertEqual(StockMovement.objects.filter(kind='sale').count(),1)
    def test_two_sales_cannot_overdraw(self):
        lot=self.received(5);a=self.sale(3);b=self.sale(3);self.run_parallel([a.pk,b.pk])
        if not Payment.objects.exists():services.validate_sale(self.user,a.pk)
        lot.refresh_from_db();self.assertEqual(lot.quantity,2);self.assertEqual(Payment.objects.count(),1)
