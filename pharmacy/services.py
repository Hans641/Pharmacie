"""Toutes les mutations commerciales passent par ces transactions atomiques."""
from decimal import Decimal
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import *


def require(user, permission):
    if not user.is_active or not user.has_perm('pharmacy.'+permission):
        raise PermissionDenied


def audit(user, action, obj):
    AuditLog.objects.create(author=user,action=action,target=f'{obj._meta.label} #{obj.pk} — {obj}')


def positive(value):
    if isinstance(value,bool) or not isinstance(value,int) or value <= 0:
        raise ValidationError('La quantité doit être un entier strictement positif.')


@transaction.atomic
def add_purchase_line(user,purchase_id,medicine,quantity,unit_price):
    require(user,'change_purchase')
    positive(quantity)
    purchase=Purchase.objects.select_for_update().get(pk=purchase_id)
    if purchase.status != Purchase.Status.DRAFT:
        raise ValidationError('Seule une commande en brouillon peut être modifiée.')
    if not medicine.active or unit_price <= 0:
        raise ValidationError('Médicament inactif ou prix invalide.')
    line=PurchaseLine(purchase=purchase,medicine=medicine,quantity=quantity,unit_price=unit_price)
    line.full_clean();line.save();audit(user,'Ajout de ligne achat',purchase)
    return line


@transaction.atomic
def remove_purchase_line(user,purchase_id,line_id):
    require(user,'change_purchase')
    purchase=Purchase.objects.select_for_update().get(pk=purchase_id)
    if purchase.status != Purchase.Status.DRAFT:
        raise ValidationError('Seule une commande en brouillon peut être modifiée.')
    purchase.lines.get(pk=line_id).delete()
    audit(user,'Retrait de ligne achat',purchase)


@transaction.atomic
def order_purchase(user,purchase_id,cancel=False):
    require(user,'change_purchase')
    p=Purchase.objects.select_for_update().get(pk=purchase_id)
    if cancel:
        if p.status not in [Purchase.Status.DRAFT,Purchase.Status.ORDERED] or p.receipts.exists():
            raise ValidationError('Une commande réceptionnée ne peut pas être annulée.')
        p.status=Purchase.Status.CANCELLED
    else:
        if p.status != Purchase.Status.DRAFT or not p.lines.exists() or not p.supplier.active:
            raise ValidationError('La commande doit être un brouillon non vide avec un fournisseur actif.')
        p.status=Purchase.Status.ORDERED
    p.save(update_fields=['status']);audit(user,'Annulation achat' if cancel else 'Validation achat',p)
    return p


@transaction.atomic
def receive_purchase(user,purchase_id,items,token):
    require(user,'receive_purchase')
    existing=Receipt.objects.filter(token=token).first()
    if existing:
        if existing.purchase_id != purchase_id: raise ValidationError('Référence de réception déjà utilisée.')
        return existing
    p=Purchase.objects.select_for_update().get(pk=purchase_id)
    if p.status not in [Purchase.Status.ORDERED,Purchase.Status.PARTIAL]:
        raise ValidationError('Cette commande ne peut pas être réceptionnée.')
    if not items: raise ValidationError('Ajoutez au moins une ligne de réception.')
    receipt=Receipt.objects.create(purchase=p,author=user,token=token)
    for item in items:
        qty=item['quantity'];positive(qty)
        line=p.lines.select_for_update().get(pk=item['line_id'])
        if qty>line.remaining: raise ValidationError('Quantité reçue supérieure au reliquat de commande.')
        if not item['number'].strip(): raise ValidationError('Numéro de lot obligatoire.')
        if item['expires_on'] < timezone.localdate(): raise ValidationError('Impossible de réceptionner un lot périmé.')
        lot,created=Lot.objects.get_or_create(medicine=line.medicine,number=item['number'].strip(),defaults={'expires_on':item['expires_on'],'unit_cost':line.unit_price})
        if lot.expires_on != item['expires_on'] or lot.unit_cost != line.unit_price:
            raise ValidationError('Ce lot existe avec une autre péremption ou un autre coût.')
        updated=PurchaseLine.objects.filter(pk=line.pk,received__lte=F('quantity')-qty).update(received=F('received')+qty)
        if updated!=1: raise ValidationError('Le reliquat a changé. Rechargez la commande.')
        Lot.objects.filter(pk=lot.pk).update(quantity=F('quantity')+qty,received_quantity=F('received_quantity')+qty)
        ReceiptLine.objects.create(receipt=receipt,purchase_line=line,lot=lot,quantity=qty,unit_cost=line.unit_price)
        StockMovement.objects.create(lot=lot,quantity=qty,kind='receipt',reason=str(receipt),receipt=receipt,author=user)
    p.status=Purchase.Status.PARTIAL if p.lines.filter(received__lt=F('quantity')).exists() else Purchase.Status.RECEIVED
    p.save(update_fields=['status']);audit(user,'Réception achat',receipt)
    return receipt


@transaction.atomic
def add_sale_line(user,sale_id,medicine,quantity,lot_id=None):
    require(user,'change_sale');positive(quantity)
    sale=Sale.objects.select_for_update().get(pk=sale_id)
    if sale.status != Sale.Status.DRAFT: raise ValidationError('Cette vente est déjà validée.')
    if not medicine.active or not medicine.authorized: raise ValidationError('Ce médicament n’est pas autorisé à la délivrance.')
    lots=medicine.lots.filter(blocked=False,expires_on__gte=timezone.localdate(),quantity__gt=0).order_by('expires_on','pk')
    if lot_id: lots=lots.filter(pk=lot_id)
    remaining=quantity
    for lot in lots:
        reserved=sale.lines.filter(lot=lot).aggregate(n=models.Sum('quantity'))['n'] or 0
        take=min(remaining,max(0,lot.quantity-reserved))
        if take:
            SaleLine.objects.create(sale=sale,lot=lot,quantity=take,unit_price=medicine.sale_price,unit_cost=lot.unit_cost)
            remaining-=take
        if remaining==0: break
    if remaining: raise ValidationError('Stock délivrable insuffisant. Aucun ajout effectué.')
    audit(user,'Ajout au panier',sale)


@transaction.atomic
def remove_sale_line(user,sale_id,line_id):
    require(user,'change_sale')
    sale=Sale.objects.select_for_update().get(pk=sale_id)
    if sale.status != Sale.Status.DRAFT: raise ValidationError('Cette vente est déjà validée.')
    sale.lines.get(pk=line_id).delete();audit(user,'Retrait du panier',sale)


@transaction.atomic
def validate_sale(user,sale_id,method='cash',reference='',verified=False,prescription_checked=False):
    require(user,'validate_sale')
    sale=Sale.objects.select_for_update().get(pk=sale_id)
    if sale.status == Sale.Status.VALIDATED: return sale
    if method not in dict(Payment.METHODS): raise ValidationError('Mode de paiement invalide.')
    if method!='cash':
        require(user,'verify_payment')
        if not verified or not reference.strip(): raise ValidationError('Vérifiez le paiement auprès du prestataire et renseignez sa référence avant validation.')
    lines=list(sale.lines.select_related('lot__medicine'))
    if not lines: raise ValidationError('Le panier est vide.')
    for line in lines:
        med=line.lot.medicine
        if not med.active or not med.authorized: raise ValidationError('Un médicament du panier est inactif ou non autorisé.')
        if med.requires_prescription and not prescription_checked: raise ValidationError('Contrôlez l’ordonnance avant de valider.')
        positive(line.quantity)
        updated=Lot.objects.filter(pk=line.lot_id,blocked=False,expires_on__gte=timezone.localdate(),quantity__gte=line.quantity).update(quantity=F('quantity')-line.quantity)
        if updated!=1: raise ValidationError('Stock insuffisant, lot périmé ou bloqué. Rechargez le panier.')
        StockMovement.objects.create(lot=line.lot,quantity=-line.quantity,kind='sale',reason=str(sale),sale=sale,author=user)
    sale.status=Sale.Status.VALIDATED;sale.validated_at=timezone.now();sale.prescription_checked=prescription_checked
    sale.save(update_fields=['status','validated_at','prescription_checked'])
    Payment.objects.create(sale=sale,method=method,amount=sale.total,confirmed=True,reference=reference.strip(),verified_by=user)
    audit(user,'Validation vente et encaissement',sale)
    return sale


@transaction.atomic
def return_sale(user,line_id,quantity,reason,restock,refund_reference,token):
    require(user,'return_sale');positive(quantity)
    existing=SaleReturn.objects.filter(token=token).first()
    if existing:
        if existing.line_id!=line_id: raise ValidationError('Référence de retour déjà utilisée.')
        return existing
    line=SaleLine.objects.select_for_update().select_related('sale','lot').get(pk=line_id)
    if line.sale.status!=Sale.Status.VALIDATED: raise ValidationError('La vente doit être validée.')
    if not reason.strip() or not refund_reference.strip(): raise ValidationError('Motif et référence du remboursement obligatoires.')
    if restock and (line.lot.blocked or line.lot.expired): raise ValidationError('Un lot périmé ou bloqué ne peut pas être remis en stock.')
    if SaleLine.objects.filter(pk=line.pk,returned__lte=F('quantity')-quantity).update(returned=F('returned')+quantity)!=1:
        raise ValidationError('Quantité supérieure à la quantité encore retournable.')
    result=SaleReturn.objects.create(sale=line.sale,line=line,quantity=quantity,reason=reason,restock=restock,amount=quantity*line.unit_price,refund_reference=refund_reference,token=token,author=user)
    if restock:
        Lot.objects.filter(pk=line.lot_id).update(quantity=F('quantity')+quantity)
        StockMovement.objects.create(lot=line.lot,quantity=quantity,kind='return',reason=reason[:250],sale=line.sale,return_record=result,author=user)
    audit(user,'Retour et remboursement',result)
    return result


@transaction.atomic
def adjust_stock(user,lot_id,counted,reason,blocked):
    require(user,'adjust_stock')
    if not isinstance(counted,int) or counted<0 or not reason.strip(): raise ValidationError('Quantité positive ou nulle et motif obligatoires.')
    lot=Lot.objects.select_for_update().get(pk=lot_id)
    delta=counted-lot.quantity
    StockMovement.objects.create(lot=lot,quantity=delta,kind='inventory',reason=reason[:250],author=user)
    lot.quantity=counted;lot.blocked=blocked;lot.save(update_fields=['quantity','blocked'])
    audit(user,'Inventaire / statut lot',lot)
    return lot
