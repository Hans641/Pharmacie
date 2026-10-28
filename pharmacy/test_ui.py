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
