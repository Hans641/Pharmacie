import uuid
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

POSITIVE = MinValueValidator(Decimal('0.01'))

def validate_photo(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError('La photo ne doit pas dépasser 5 Mo.')

class Category(models.Model):
    name = models.CharField('Nom', max_length=120, unique=True)
    description = models.TextField('Description', blank=True)
    class Meta:
        ordering = ['name']; verbose_name = 'catégorie'
    def __str__(self): return self.name

class Medicine(models.Model):
    name = models.CharField('Nom commercial', max_length=180)
    generic_name = models.CharField('Dénomination générique', max_length=180, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Catégorie')
    form = models.CharField('Forme pharmaceutique', max_length=100)
    dosage = models.CharField('Dosage', max_length=80, blank=True)
    manufacturer = models.CharField('Laboratoire', max_length=180, blank=True)
    barcode = models.CharField('Code-barres', max_length=80, unique=True, null=True, blank=True)
    photo = models.ImageField('Photo', upload_to='medicaments/%Y/%m/', blank=True, validators=[validate_photo, FileExtensionValidator(['jpg','jpeg','png','webp'])])
    purchase_price = models.DecimalField("Prix d'achat (Ar)", max_digits=14, decimal_places=2, validators=[POSITIVE])
    sale_price = models.DecimalField('Prix de vente (Ar)', max_digits=14, decimal_places=2, validators=[POSITIVE])
    threshold = models.PositiveIntegerField("Seuil d'alerte", default=10)
    active = models.BooleanField('Actif', default=True)
    requires_prescription = models.BooleanField('Ordonnance requise', default=False)
    authorized = models.BooleanField('Délivrance autorisée par le responsable', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['name']; verbose_name = 'médicament'
        constraints = [models.CheckConstraint(condition=Q(purchase_price__gt=0, sale_price__gt=0),name='medicine_positive_prices')]
    def clean(self):
        self.barcode = self.barcode or None
    def __str__(self): return f'{self.name} {self.dosage}'.strip()
    @property
    def available(self):
        return self.lots.filter(blocked=False, expires_on__gte=timezone.localdate()).aggregate(n=models.Sum('quantity'))['n'] or 0

class Supplier(models.Model):
    name = models.CharField('Raison sociale', max_length=180)
    address = models.TextField('Adresse', blank=True)
    phone = models.CharField('Téléphone', max_length=40)
    email = models.EmailField('E-mail', blank=True)
    tax_id = models.CharField('Identifiant fiscal', max_length=100, blank=True)
    contact = models.CharField('Contact principal', max_length=180, blank=True)
    active = models.BooleanField('Actif', default=True)
    class Meta:
        ordering = ['name']; verbose_name = 'fournisseur'
    def __str__(self): return self.name

class Customer(models.Model):
    name = models.CharField('Nom', max_length=180)
    phone = models.CharField('Téléphone', max_length=40, blank=True)
    address = models.CharField('Coordonnées', max_length=250, blank=True)
    active = models.BooleanField('Actif', default=True)
    class Meta:
        ordering = ['name']; verbose_name = 'client'
    def __str__(self): return self.name

class Purchase(models.Model):
    class Status(models.TextChoices):
        DRAFT='draft','Brouillon'
        ORDERED='ordered','Commandée'
        PARTIAL='partial','Partiellement réceptionnée'
        RECEIVED='received','Entièrement réceptionnée'
        CANCELLED='cancelled','Annulée'
    supplier = models.ForeignKey(Supplier,on_delete=models.PROTECT,verbose_name='Fournisseur')
    status = models.CharField(max_length=12,choices=Status,default=Status.DRAFT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']; verbose_name="commande d'achat"
        permissions=[('receive_purchase','Réceptionner les commandes')]
    def __str__(self): return f'ACH-{self.pk:06d}' if self.pk else 'Nouvelle commande'
    @property
    def total(self): return sum((l.quantity*l.unit_price for l in self.lines.all()),Decimal('0'))

class PurchaseLine(models.Model):
    purchase = models.ForeignKey(Purchase,on_delete=models.PROTECT,related_name='lines')
    medicine = models.ForeignKey(Medicine,on_delete=models.PROTECT,verbose_name='Médicament')
    quantity = models.PositiveIntegerField('Quantité commandée',validators=[MinValueValidator(1)])
    received = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField("Prix d'achat (Ar)",max_digits=14,decimal_places=2,validators=[POSITIVE])
    class Meta:
        constraints=[models.CheckConstraint(condition=Q(quantity__gt=0,unit_price__gt=0,received__lte=models.F('quantity')),name='purchase_line_valid')]
    def __str__(self): return f'{self.purchase} · {self.medicine}'
    @property
    def remaining(self): return self.quantity-self.received
    @property
    def subtotal(self): return self.quantity*self.unit_price

class Lot(models.Model):
    medicine = models.ForeignKey(Medicine,on_delete=models.PROTECT,related_name='lots',verbose_name='Médicament')
    number = models.CharField('Numéro de lot',max_length=100)
    expires_on = models.DateField('Date de péremption')
    quantity = models.PositiveIntegerField('Stock physique',default=0)
    received_quantity = models.PositiveIntegerField('Quantité reçue',default=0)
    unit_cost = models.DecimalField(max_digits=14,decimal_places=2,validators=[POSITIVE])
    blocked = models.BooleanField('Bloqué',default=False)
    class Meta:
        ordering=['expires_on','pk']; verbose_name='lot'
        constraints=[models.UniqueConstraint(fields=['medicine','number'],name='unique_medicine_lot'),models.CheckConstraint(condition=Q(quantity__gte=0,unit_cost__gt=0),name='lot_valid')]
        permissions=[('adjust_stock','Corriger les inventaires')]
    def __str__(self): return f'{self.medicine} · lot {self.number} · {self.quantity} unités'
    @property
    def expired(self): return self.expires_on < timezone.localdate()

class Receipt(models.Model):
    purchase = models.ForeignKey(Purchase,on_delete=models.PROTECT,related_name='receipts')
    token = models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']; verbose_name='réception'
    def __str__(self): return f'REC-{self.pk:06d}'
    @property
    def total(self): return sum((l.quantity*l.unit_cost for l in self.lines.all()),Decimal('0'))

class ReceiptLine(models.Model):
    receipt = models.ForeignKey(Receipt,on_delete=models.PROTECT,related_name='lines')
    purchase_line = models.ForeignKey(PurchaseLine,on_delete=models.PROTECT)
    lot = models.ForeignKey(Lot,on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_cost = models.DecimalField(max_digits=14,decimal_places=2,validators=[POSITIVE])
    class Meta:
        constraints=[models.CheckConstraint(condition=Q(quantity__gt=0,unit_cost__gt=0),name='receipt_line_valid')]

class Sale(models.Model):
    class Status(models.TextChoices):
        DRAFT='draft','Brouillon'
        VALIDATED='validated','Validée'
    customer = models.ForeignKey(Customer,null=True,blank=True,on_delete=models.PROTECT,verbose_name='Client')
    status = models.CharField(max_length=12,choices=Status,default=Status.DRAFT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True,blank=True)
    prescription_checked = models.BooleanField('Ordonnance contrôlée par le professionnel',default=False)
    class Meta:
        ordering=['-created_at']; verbose_name='vente'
        permissions=[('validate_sale','Valider une vente'),('return_sale','Autoriser un retour'),('verify_payment','Vérifier un paiement électronique')]
    def __str__(self): return f'VEN-{self.pk:06d}' if self.pk else 'Nouvelle vente'
    @property
    def total(self): return sum((l.quantity*l.unit_price for l in self.lines.all()),Decimal('0'))
    @property
    def refunded(self): return sum((r.amount for r in self.returns.all()),Decimal('0'))

class SaleLine(models.Model):
    sale = models.ForeignKey(Sale,on_delete=models.PROTECT,related_name='lines')
    lot = models.ForeignKey(Lot,on_delete=models.PROTECT,verbose_name='Lot délivré')
    quantity = models.PositiveIntegerField('Quantité',validators=[MinValueValidator(1)])
    returned = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=14,decimal_places=2,validators=[POSITIVE])
    unit_cost = models.DecimalField(max_digits=14,decimal_places=2,validators=[POSITIVE])
    class Meta:
        constraints=[models.CheckConstraint(condition=Q(quantity__gt=0,unit_price__gt=0,unit_cost__gt=0,returned__lte=models.F('quantity')),name='sale_line_valid')]
    @property
    def subtotal(self): return self.quantity*self.unit_price
    def __str__(self): return f'{self.lot.medicine} · lot {self.lot.number}'

class Payment(models.Model):
    METHODS=[('cash','Espèces'),('mobile','Mobile money'),('card','Carte / virement')]
    sale = models.OneToOneField(Sale,on_delete=models.PROTECT,related_name='payment')
    method = models.CharField('Mode de paiement',max_length=10,choices=METHODS)
    amount = models.DecimalField(max_digits=14,decimal_places=2,validators=[POSITIVE])
    confirmed = models.BooleanField(default=False)
    reference = models.CharField('Référence de transaction vérifiée',max_length=160,blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.CheckConstraint(condition=Q(amount__gt=0),name='payment_positive')]

class SaleReturn(models.Model):
    sale = models.ForeignKey(Sale,on_delete=models.PROTECT,related_name='returns')
    line = models.ForeignKey(SaleLine,on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField('Quantité',validators=[MinValueValidator(1)])
    reason = models.TextField('Motif')
    restock = models.BooleanField('Éligible à la remise en stock',default=False)
    amount = models.DecimalField(max_digits=14,decimal_places=2)
    refund_reference = models.CharField('Référence du remboursement effectué',max_length=160)
    token = models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']; verbose_name='retour de vente'
        constraints=[models.CheckConstraint(condition=Q(quantity__gt=0,amount__gt=0),name='return_valid')]

class StockMovement(models.Model):
    lot = models.ForeignKey(Lot,on_delete=models.PROTECT,related_name='movements')
    quantity = models.IntegerField('Variation')
    kind = models.CharField('Nature',max_length=20,choices=[('receipt','Réception'),('sale','Vente'),('return','Retour'),('inventory','Inventaire'),('block','Blocage / déblocage')])
    reason = models.CharField('Motif / référence',max_length=250)
    receipt = models.ForeignKey(Receipt,null=True,on_delete=models.PROTECT)
    sale = models.ForeignKey(Sale,null=True,on_delete=models.PROTECT)
    return_record = models.ForeignKey(SaleReturn,null=True,on_delete=models.PROTECT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']; verbose_name='mouvement de stock'

class AuditLog(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']; verbose_name="journal d'audit"
