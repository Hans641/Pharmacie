"""Contrats de présentation : français, permissions et repli HTML natif."""
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import Group
from django.template import Template, Context
from django.utils import timezone
from .tests import Fixtures
from django.test import TestCase
from .forms import MedicineForm
from .models import Sale
from .management.commands.setup_roles import setup_roles
from .templatetags.ui import money, expiry_state

class PresentationTests(Fixtures, TestCase):
    def setUp(self):
        self.make_data()
        self.client.force_login(self.user)

    def test_local_assets_and_active_navigation(self):
        response=self.client.get('/catalogue/medicaments/')
        self.assertContains(response,'/static/css/vendor/bootstrap.min.css')
        self.assertContains(response,'/static/js/app.js')
        self.assertNotContains(response,'cdn.jsdelivr.net')
        self.assertContains(response,'aria-current="page"')
        self.assertContains(response,'href="#main-content"')
        self.assertNotContains(response,'hero-strip')

    def test_french_money_and_expiry_boundaries(self):
        self.assertEqual(money(Decimal('15000')), '15\u202f000,00 Ar')
        self.assertEqual(money(Decimal('-1.50')), '-1,50 Ar')
        self.assertEqual(money(None), '—')
        today=timezone.localdate()
        for days,state in [(-1,'expired'),(0,'soon'),(90,'soon'),(91,'valid')]:
            self.assertEqual(expiry_state(today+timedelta(days=days)),state)

    def test_catalogue_formats_decimal_instead_of_preformatted_cell(self):
        self.med.sale_price=Decimal('15000');self.med.save()
        response=self.client.get('/catalogue/medicaments/')
        self.assertContains(response,'15\u202f000,00 Ar')
        self.assertNotContains(response,'15,000.00 Ar')
        self.assertContains(response,'data-label="Prix de vente"')

    def test_form_error_describes_field_and_preserves_value(self):
        response=self.client.post('/catalogue/medicaments/ajouter/',{'name':'Produit conservé','purchase_price':'-2'})
        self.assertContains(response,'data-error-summary')
        self.assertContains(response,'id_purchase_price_errors')
        self.assertContains(response,'aria-invalid="true"')
        self.assertContains(response,'Produit conservé')
        self.assertContains(response,'name="csrfmiddlewaretoken"')

    def test_cashier_does_not_see_electronic_or_return_actions(self):
        setup_roles();self.other.groups.add(Group.objects.get(name='Caissier'))
        self.received();sale=self.sale();self.client.force_login(self.other)
        response=self.client.get(f'/ventes/{sale.pk}/')
        self.assertContains(response,'name="action" value="validate"')
        self.assertContains(response,'name="method" value="cash"')
        self.assertNotContains(response,'name="method" value="mobile"')
        self.assertNotContains(response,'name="verified"')
        self.assertNotContains(response,'Enregistrer un retour')
        self.assertContains(response,'name="action" value="add"')

    def test_read_only_role_cannot_see_mutation_controls(self):
        setup_roles();self.other.groups.add(Group.objects.get(name='Responsable de gestion'))
        self.received();sale=self.sale();self.client.force_login(self.other)
        response=self.client.get(f'/ventes/{sale.pk}/')
        self.assertNotContains(response,'name="action" value="add"')
        self.assertNotContains(response,'name="action" value="validate"')
        self.assertNotContains(response,'data-cash-tools')
        response=self.client.get('/stocks/')
        self.assertNotContains(response,'Inventaire / blocage')

    def test_managed_admin_does_not_see_superuser_edit_link(self):
        setup_roles();self.other.groups.add(Group.objects.get(name='Administrateur'))
        self.client.force_login(self.other)
        response=self.client.get('/utilisateurs/')
        self.assertNotContains(response,f'href="/utilisateurs/{self.user.pk}/"')
        self.assertContains(response,f'href="/utilisateurs/{self.other.pk}/"')

    def test_filter_chip_removal_preserves_other_filters(self):
        response=self.client.get('/catalogue/medicaments/',{'q':'Produit','status':'active','sort':'stock'})
        self.assertContains(response,'Filtres actifs')
        self.assertContains(response,'?status=active&amp;sort=stock')
        self.assertContains(response,'data-live-search')

    def test_blocked_and_expired_are_both_visible(self):
        lot=self.received()
        lot.expires_on=timezone.localdate()-timedelta(days=1);lot.blocked=True;lot.save()
        response=self.client.get('/stocks/')
        self.assertContains(response,'Bloqué')
        self.assertContains(response,'Périmé')
        self.assertContains(response,'data-label="Péremption"')

    def test_receipt_and_return_context_use_actual_remaining_quantities(self):
        lot=self.received();sale=self.sale()
        from . import services
        services.validate_sale(self.user,sale.pk)
        response=self.client.get(f'/ventes/{sale.pk}/retour/')
        self.assertContains(response,'encore retournable : 3')
        self.assertContains(response,'name="token"')
        response=self.client.get(f'/stocks/{lot.pk}/inventaire/')
        self.assertContains(response,'17 unités')

    def test_validated_sale_offers_receipt_and_next_sale(self):
        self.received();sale=self.sale()
        from . import services
        services.validate_sale(self.user,sale.pk)
        response=self.client.get(f'/ventes/{sale.pk}/')
        self.assertContains(response,'Télécharger le reçu PDF')
        self.assertContains(response,'href="/ventes/nouvelle/"')
        self.assertContains(response,'data-print')
        self.assertNotContains(response,'data-checkout')

class ProgressiveFormTests(Fixtures, TestCase):
    def setUp(self):
        self.make_data()
        self.client.force_login(self.user)

    def test_medicine_has_three_steps_and_native_no_js_fallback(self):
        response = self.client.get('/catalogue/medicaments/ajouter/')
        self.assertContains(response, 'data-wizard-step', count=3)
        self.assertContains(response, 'data-wizard-summary')
        self.assertContains(response, 'data-wizard-progress hidden')
        self.assertContains(response, 'data-wizard-submit>')
        self.assertNotContains(response, 'novalidate')
        self.assertNotContains(response, 'data-wizard-step hidden')
        self.assertContains(response, 'Créer le médicament')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_price_constraints_and_inline_feedback_are_exposed(self):
        response = self.client.get('/catalogue/medicaments/ajouter/')
        self.assertContains(response, 'min="0.01"', count=2)
        self.assertContains(response, 'id_purchase_price_feedback')
        self.assertContains(response, 'data-field-label="Prix de vente (Ar)"')
        self.assertContains(response, 'inputmode="decimal"')
        self.assertContains(response, 'son unicité sera vérifiée')

    def test_photo_has_local_guidance_and_current_file_metadata(self):
        self.med.photo = 'medicaments/demo.png'
        self.med.save()
        response = self.client.get(f'/catalogue/medicaments/{self.med.pk}/modifier/')
        self.assertContains(response, 'data-current-file="demo.png"')
        self.assertContains(response, 'data-max-bytes="5242880"')
        self.assertContains(response, 'accept=".jpg,.jpeg,.png,.webp"')
        self.assertContains(response, 'Enregistrer les modifications')

    def test_server_errors_survive_on_all_steps_without_saving(self):
        from .models import Medicine
        before = Medicine.objects.count()
        response = self.client.post('/catalogue/medicaments/ajouter/', {
            'name': 'Nom conservé', 'category': self.category.pk, 'form': 'Comprimé',
            'purchase_price': '-1', 'sale_price': '2', 'threshold': '10',
        })
        self.assertEqual(Medicine.objects.count(), before)
        self.assertContains(response, 'Nom conservé')
        self.assertContains(response, 'Au dernier envoi')
        self.assertContains(response, 'data-server-errors')
        self.assertContains(response, 'id_purchase_price_errors')
        self.assertContains(response, 'data-wizard-step', count=3)

    def test_other_forms_remain_single_screen(self):
        response = self.client.get('/catalogue/fournisseurs/ajouter/')
        self.assertNotContains(response, 'data-wizard-step')
        self.assertNotContains(response, 'data-wizard-progress')
        self.assertContains(response, 'data-field-feedback')
        self.assertContains(response, '/static/js/forms.js')

    def test_success_is_dismissible_but_errors_are_persistent(self):
        response = self.client.post('/catalogue/categories/ajouter/', {
            'name': 'Catégorie UI', 'description': '',
        }, follow=True)
        self.assertContains(response, 'data-toast')
        self.assertContains(response, 'data-dismiss-toast')
        self.assertContains(response, 'role="status"')
        self.assertNotContains(response, 'autohide')
        # Catégorie utilisée : l'erreur reste une alerte persistante, sans bouton de toast.
        response = self.client.post(f'/catalogue/categories/{self.category.pk}/archiver/', follow=True)
        self.assertContains(response, 'role="alert"')
        self.assertNotContains(response, 'data-dismiss-toast')

    def test_loading_placeholder_is_local_and_hidden_before_search(self):
        response = self.client.get('/catalogue/medicaments/')
        self.assertContains(response, 'data-search-loading hidden')
        self.assertContains(response, 'class="skeleton-line"', count=2)
        self.assertContains(response, '/static/css/experience.css')
        self.assertNotContains(response, 'cdn.jsdelivr.net')

class OperationPresentationTests(Fixtures, TestCase):
    def control_names(self, response):
        from html.parser import HTMLParser
        class Controls(HTMLParser):
            def __init__(self):
                super().__init__()
                self.names = []
            def handle_starttag(self, tag, attrs):
                if tag in ['input', 'select', 'textarea']:
                    name = dict(attrs).get('name')
                    if name: self.names.append(name)
        parser = Controls()
        parser.feed(response.content.decode())
        return parser.names

    def setUp(self):
        self.make_data()
        self.client.force_login(self.user)

    def test_partial_receipt_exposes_remaining_and_exact_cost(self):
        import uuid
        from . import services
        p, line = self.purchase()
        services.order_purchase(self.user, p.pk)
        services.receive_purchase(self.user, p.pk, [{
            'line_id': line.pk, 'quantity': 8, 'number': 'PARTIAL-UI',
            'expires_on': timezone.localdate() + timedelta(days=100),
        }], uuid.uuid4())
        response = self.client.get(f'/achats/{p.pk}/reception/')
        self.assertContains(response, 'data-operation="receipt"')
        self.assertContains(response, 'data-remaining="12"')
        self.assertContains(response, 'data-unit-minor="1000"')
        self.assertContains(response, 'Traçabilité du lot')
        self.assertContains(response, 'Valeur de cette réception')
        self.assertContains(response, 'name="token"')
        self.assertEqual(self.med.available, 8)

    def test_inventory_snapshot_and_single_page_fallback(self):
        lot = self.received()
        response = self.client.get(f'/stocks/{lot.pk}/inventaire/')
        self.assertContains(response, 'data-operation="inventory"')
        self.assertContains(response, 'data-stock-before="20"')
        self.assertContains(response, 'Correction prévue')
        self.assertContains(response, 'data-operation-preview hidden')
        self.assertEqual(self.control_names(response).count('confirm'), 1)
        self.assertContains(response, 'name="counted"')
        self.assertNotContains(response, 'data-wizard-step')
        self.assertNotContains(response, 'novalidate')
        lot.refresh_from_db()
        self.assertEqual(lot.quantity, 20)

    def test_return_exposes_actual_balance_and_lot_eligibility(self):
        import uuid
        from . import services
        lot = self.received()
        sale = self.sale()
        services.validate_sale(self.user, sale.pk)
        services.return_sale(self.user, sale.lines.get().pk, 1, 'Motif', False, 'REF-UI', uuid.uuid4())
        lot.blocked = True
        lot.expires_on = timezone.localdate() - timedelta(days=1)
        lot.save()
        response = self.client.get(f'/ventes/{sale.pk}/retour/')
        self.assertContains(response, 'data-operation="return"')
        self.assertContains(response, 'data-remaining="2"')
        self.assertContains(response, 'data-unit-minor="2000"')
        self.assertContains(response, 'data-blocked="1"')
        self.assertContains(response, 'data-expires="' + lot.expires_on.isoformat() + '"')
        self.assertContains(response, 'Remboursement à consigner')
        self.assertContains(response, 'Remboursement effectué')
        self.assertContains(response, 'name="refund_reference"')
        self.assertEqual(self.med.available, 0)  # lot désormais bloqué et périmé

    def test_receipt_over_limit_still_refused_by_server_without_js(self):
        import uuid
        from . import services
        from .models import Receipt, StockMovement
        p, line = self.purchase()
        services.order_purchase(self.user, p.pk)
        response = self.client.post(f'/achats/{p.pk}/reception/', {
            'line': line.pk, 'quantity': 21, 'number': 'EXCESS-UI',
            'expires_on': (timezone.localdate() + timedelta(days=100)).isoformat(),
            'token': str(uuid.uuid4()), 'confirm': 'on',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'role="alert"')
        self.assertFalse(Receipt.objects.exists())
        self.assertFalse(StockMovement.objects.exists())
        self.assertEqual(self.med.available, 0)

    def test_return_over_limit_still_refused_by_server_without_js(self):
        import uuid
        from . import services
        from .models import SaleReturn
        lot = self.received()
        sale = self.sale()
        services.validate_sale(self.user, sale.pk)
        response = self.client.post(f'/ventes/{sale.pk}/retour/', {
            'line': sale.lines.get().pk, 'quantity': 4, 'reason': 'Quantité excessive',
            'refund_reference': 'REF-INVALID', 'token': str(uuid.uuid4()), 'confirm': 'on',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'role="alert"')
        self.assertFalse(SaleReturn.objects.exists())
        lot.refresh_from_db()
        self.assertEqual(lot.quantity, 17)

    def test_unauthorized_users_never_receive_operation_data(self):
        from . import services
        lot = self.received()
        sale = self.sale()
        services.validate_sale(self.user, sale.pk)
        p = lot.movements.filter(kind='receipt').first().receipt.purchase
        self.client.force_login(self.other)
        for url in [f'/achats/{p.pk}/reception/', f'/stocks/{lot.pk}/inventaire/', f'/ventes/{sale.pk}/retour/']:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)
                self.assertNotContains(response, 'data-operation-line', status_code=403)
                self.assertNotContains(response, 'data-stock-before', status_code=403)

    def test_minor_units_never_rounds_or_uses_float(self):
        from .templatetags.ui import minor_units
        self.assertEqual(minor_units(Decimal('1500.05')), '150005')
        self.assertEqual(minor_units(Decimal('999999999999.99')), '99999999999999')
        self.assertEqual(minor_units(Decimal('0')), '0')
        self.assertEqual(minor_units(Decimal('1.001')), '')
        self.assertEqual(minor_units(Decimal('NaN')), '')
        self.assertEqual(minor_units(None), '')

    def test_operational_groups_preserve_all_post_fields_and_local_module(self):
        p, line = self.purchase()
        from . import services
        services.order_purchase(self.user, p.pk)
        response = self.client.get(f'/achats/{p.pk}/reception/')
        for name in ['line', 'quantity', 'number', 'expires_on', 'token', 'confirm']:
            self.assertEqual(self.control_names(response).count(name), 1)
        self.assertContains(response, 'Articles reçus')
        self.assertContains(response, 'type="module" src="/static/js/operations.js"')
        self.assertContains(response, 'id="confirm-submit"')
