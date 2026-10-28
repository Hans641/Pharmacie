from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from django.utils import timezone
from .models import *

class StyledForm:
    def style(self):
        for field in self.fields.values():
            field.widget.attrs['class']='form-check-input' if isinstance(field.widget,forms.CheckboxInput) else 'form-control'
            if isinstance(field.widget,forms.DateInput): field.widget.input_type='date'

class EntityForm(StyledForm,forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.style()

class MedicineForm(EntityForm):
    class Meta:
        model=Medicine
        exclude=['created_at']
    def clean_barcode(self): return self.cleaned_data.get('barcode') or None

class CategoryForm(EntityForm):
    class Meta: model=Category;fields='__all__'
class SupplierForm(EntityForm):
    class Meta: model=Supplier;fields='__all__'
class CustomerForm(EntityForm):
    class Meta: model=Customer;fields='__all__'
class PurchaseForm(EntityForm):
    class Meta: model=Purchase;fields=['supplier']
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.fields['supplier'].queryset=Supplier.objects.filter(active=True)
class PurchaseLineForm(EntityForm):
    class Meta: model=PurchaseLine;fields=['medicine','quantity','unit_price']
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.fields['medicine'].queryset=Medicine.objects.filter(active=True)
class SaleForm(EntityForm):
    class Meta: model=Sale;fields=['customer']
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.fields['customer'].queryset=Customer.objects.filter(active=True)
class BasicForm(StyledForm,forms.Form):
    def __init__(self,*a,**kw): super().__init__(*a,**kw);self.style()
class CartForm(BasicForm):
    medicine=forms.ModelChoiceField(label='Médicament',queryset=Medicine.objects.none())
    quantity=forms.IntegerField(label='Quantité',min_value=1)
    lot=forms.ModelChoiceField(label='Lot spécifique (facultatif, FEFO par défaut)',queryset=Lot.objects.none(),required=False)
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.fields['medicine'].queryset=Medicine.objects.filter(active=True,authorized=True)
        self.fields['lot'].queryset=Lot.objects.filter(medicine__active=True,medicine__authorized=True,blocked=False,expires_on__gte=timezone.localdate(),quantity__gt=0).select_related('medicine')
    def clean(self):
        data=super().clean()
        if data.get('lot') and data.get('medicine') and data['lot'].medicine_id!=data['medicine'].pk: self.add_error('lot','Ce lot ne correspond pas au médicament.')
        return data
class CheckoutForm(BasicForm):
    method=forms.ChoiceField(label='Mode de paiement',choices=Payment.METHODS)
    reference=forms.CharField(label='Référence du paiement électronique',required=False,max_length=160)
    verified=forms.BooleanField(label='Paiement vérifié auprès du prestataire',required=False)
    prescription_checked=forms.BooleanField(label='Ordonnance contrôlée si nécessaire',required=False)
    confirm=forms.BooleanField(label='Je confirme la délivrance et l’encaissement')
class ReceiveForm(BasicForm):
    line=forms.ModelChoiceField(label='Ligne de commande',queryset=PurchaseLine.objects.none())
    quantity=forms.IntegerField(label='Quantité reçue',min_value=1)
    number=forms.CharField(label='Numéro de lot',max_length=100)
    expires_on=forms.DateField(label='Péremption',widget=forms.DateInput(attrs={'type':'date'}))
    token=forms.UUIDField(widget=forms.HiddenInput)
    confirm=forms.BooleanField(label='Je confirme la réception effective')
    def __init__(self,*a,purchase,**kw):
        super().__init__(*a,**kw);self.fields['line'].queryset=purchase.lines.filter(received__lt=models.F('quantity')).select_related('medicine')
class ReturnForm(BasicForm):
    line=forms.ModelChoiceField(label='Ligne retournée',queryset=SaleLine.objects.none())
    quantity=forms.IntegerField(label='Quantité',min_value=1)
    reason=forms.CharField(label='Motif',widget=forms.Textarea)
    restock=forms.BooleanField(label='Produit contrôlé et éligible à la remise en stock',required=False)
    refund_reference=forms.CharField(label='Référence du remboursement effectué',max_length=160)
    token=forms.UUIDField(widget=forms.HiddenInput)
    confirm=forms.BooleanField(label='Je confirme le retour et le remboursement')
    def __init__(self,*a,sale,**kw):
        super().__init__(*a,**kw);self.fields['line'].queryset=sale.lines.all()
class InventoryForm(BasicForm):
    counted=forms.IntegerField(label='Quantité physique comptée',min_value=0)
    reason=forms.CharField(label='Motif du contrôle',max_length=250)
    blocked=forms.BooleanField(label='Bloquer le lot à la vente',required=False)
    confirm=forms.BooleanField(label='Je confirme cette correction de stock')
class AccountCreateForm(StyledForm,UserCreationForm):
    groups=forms.ModelMultipleChoiceField(label='Rôles',queryset=Group.objects.all(),required=False,widget=forms.CheckboxSelectMultiple)
    class Meta: model=User;fields=['username','first_name','last_name','email','groups','is_active']
    def __init__(self,*a,**kw): super().__init__(*a,**kw);self.style()
class AccountChangeForm(EntityForm):
    class Meta: model=User;fields=['first_name','last_name','email','groups','is_active']
    def clean_is_active(self):
        active=self.cleaned_data['is_active']
        if self.instance.is_superuser and not active: raise forms.ValidationError('La désactivation du superadministrateur doit être faite par un autre superadministrateur dans l’administration.')
        return active
