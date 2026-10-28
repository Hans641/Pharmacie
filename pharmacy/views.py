import uuid
from datetime import timedelta, date
from decimal import Decimal
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction, OperationalError
from django.db.models import Sum, F, Q, DecimalField, ExpressionWrapper
from django.db.models.deletion import ProtectedError
from django.http import Http404, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from . import forms, services
from .models import *


def gate(permission):
    def wrap(view):
        @login_required
        @wraps(view)
        def inner(request,*args,**kwargs):
            app_perm=permission if '.' in permission else 'pharmacy.'+permission
            if not request.user.has_perm(app_perm): raise PermissionDenied
            return view(request,*args,**kwargs)
        return inner
    return wrap


def error(request,exc):
    text=' '.join(exc.messages) if isinstance(exc,ValidationError) else 'Une autre opération est en cours. Rechargez la page avant de réessayer.'
    messages.error(request,text)


def page(request,query):
    return Paginator(query,15).get_page(request.GET.get('page'))


def period(request):
    today=timezone.localdate()
    try:
        start=date.fromisoformat(request.GET.get('start') or str(today.replace(day=1)))
        end=date.fromisoformat(request.GET.get('end') or str(today))
        if start>end: raise ValueError
    except ValueError:
        messages.error(request,'Période invalide : le mois en cours est affiché.')
        start,end=today.replace(day=1),today
    return start,end


def medicine_stock():
    return Medicine.objects.select_related('category').annotate(stock=Sum('lots__quantity',filter=Q(lots__blocked=False,lots__expires_on__gte=timezone.localdate()),default=0))


@login_required
def dashboard(request):
    today=timezone.localdate();start,end=period(request)
    ctx={'title':'Tableau de bord','start':start,'end':end}
    if request.user.has_perm('pharmacy.view_medicine'):
        meds=medicine_stock().filter(active=True)
        ctx.update(active_medicines=meds.count(),low_count=meds.filter(stock__lte=F('threshold')).count(),low_stock=meds.filter(stock__lte=F('threshold'))[:6])
    if request.user.has_perm('pharmacy.view_lot'):
        ctx.update(expiring=Lot.objects.filter(quantity__gt=0,expires_on__range=(today,today+timedelta(days=90))).select_related('medicine')[:6],expired_count=Lot.objects.filter(quantity__gt=0,expires_on__lt=today).count(),expiring_count=Lot.objects.filter(quantity__gt=0,expires_on__range=(today,today+timedelta(days=90))).count())
    if request.user.has_perm('pharmacy.view_sale'):
        sales=Sale.objects.filter(status='validated',validated_at__date__range=(start,end))
        lines=SaleLine.objects.filter(sale__in=sales)
        money=ExpressionWrapper(F('quantity')*F('unit_price'),output_field=DecimalField(max_digits=20,decimal_places=2))
        gross=lines.aggregate(n=Sum(money))['n'] or 0
        refunds=SaleReturn.objects.filter(created_at__date__range=(start,end)).aggregate(n=Sum('amount'))['n'] or 0
        cash=Payment.objects.filter(confirmed=True,created_at__date__range=(start,end)).aggregate(n=Sum('amount'))['n'] or 0
        ctx.update(revenue=gross,refunds=refunds,collections=cash-refunds,sales_count=sales.count(),recent_sales=sales.select_related('customer','author')[:6],top_products=lines.values('lot__medicine__name').annotate(units=Sum('quantity')).order_by('-units')[:5])
        daily=SaleLine.objects.filter(sale__status='validated',sale__validated_at__date=today).aggregate(n=Sum(money))['n'] or 0
        ctx['daily_sales']=daily
        margin=ExpressionWrapper(F('quantity')*(F('unit_price')-F('unit_cost')),output_field=DecimalField(max_digits=20,decimal_places=2))
        return_cost=ExpressionWrapper(F('quantity')*(F('line__unit_price')-F('line__unit_cost')),output_field=DecimalField(max_digits=20,decimal_places=2))
        ctx['margin']=(lines.aggregate(n=Sum(margin))['n'] or 0)-(SaleReturn.objects.filter(created_at__date__range=(start,end)).aggregate(n=Sum(return_cost))['n'] or 0)
    if request.user.has_perm('pharmacy.view_purchase'):
        receipts=ReceiptLine.objects.filter(receipt__created_at__date__range=(start,end))
        ctx['purchases_total']=receipts.aggregate(n=Sum(ExpressionWrapper(F('quantity')*F('unit_cost'),output_field=DecimalField(max_digits=20,decimal_places=2))))['n'] or 0
    return render(request,'pharmacy/dashboard.html',ctx)


ENTITIES={
    'medicaments':(Medicine,forms.MedicineForm,'Médicaments',['Nom','Catégorie','Prix de vente','Disponible','État']),
    'categories':(Category,forms.CategoryForm,'Catégories',['Nom','Description']),
    'fournisseurs':(Supplier,forms.SupplierForm,'Fournisseurs',['Raison sociale','Téléphone','E-mail','État']),
    'clients':(Customer,forms.CustomerForm,'Clients',['Nom','Téléphone','État']),
}


def entity_config(key):
    if key not in ENTITIES: raise Http404
    return ENTITIES[key]


@login_required
def entity_list(request,key):
    model,form,title,headers=entity_config(key);name=model._meta.model_name
    services.require(request.user,'view_'+name)
    query=medicine_stock() if model is Medicine else model.objects.all()
    q=request.GET.get('q','').strip()
    if q:
        filters=Q(name__icontains=q)
        if model is Medicine: filters|=Q(barcode__icontains=q)|Q(generic_name__icontains=q)
        if model in [Supplier,Customer]: filters|=Q(phone__icontains=q)
        query=query.filter(filters)
    if model is Medicine:
        category=request.GET.get('category','')
        if category.isdigit(): query=query.filter(category_id=category)
        status=request.GET.get('status','')
        if status=='active': query=query.filter(active=True)
        elif status=='archived': query=query.filter(active=False)
        sort=request.GET.get('sort','name')
        query=query.order_by(sort if sort in ['name','-name','sale_price','-sale_price','stock'] else 'name')
    p=page(request,query);rows=[]
    for obj in p:
        if model is Medicine: cells=[str(obj),obj.category,f'{obj.sale_price:,.2f} Ar',obj.stock,'Actif' if obj.active else 'Archivé']
        elif model is Category: cells=[obj.name,obj.description]
        elif model is Supplier: cells=[obj.name,obj.phone,obj.email,'Actif' if obj.active else 'Inactif']
        else: cells=[obj.name,obj.phone,'Actif' if obj.active else 'Inactif']
        rows.append({'obj':obj,'cells':cells})
    return render(request,'pharmacy/entity_list.html',{'title':title,'key':key,'rows':rows,'headers':headers,'page_obj':p,'q':q,'categories':Category.objects.all() if model is Medicine else None,'can_add':request.user.has_perm('pharmacy.add_'+name),'can_change':request.user.has_perm('pharmacy.change_'+name),'can_delete':request.user.has_perm('pharmacy.delete_'+name)})


@login_required
def entity_edit(request,key,pk=None):
    model,form_class,title,headers=entity_config(key)
    services.require(request.user,('change_' if pk else 'add_')+model._meta.model_name)
    obj=get_object_or_404(model,pk=pk) if pk else None
    form=form_class(request.POST or None,request.FILES or None,instance=obj)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            obj=form.save();services.audit(request.user,'Modification' if pk else 'Création',obj)
        messages.success(request,'Enregistrement effectué.');return redirect('entity_list',key=key)
    return render(request,'pharmacy/form.html',{'title':('Modifier' if pk else 'Ajouter')+' — '+title,'form':form,'back_url':reverse('entity_list',args=[key])})


@login_required
def entity_delete(request,key,pk):
    model,_,title,_=entity_config(key);services.require(request.user,'delete_'+model._meta.model_name)
    obj=get_object_or_404(model,pk=pk)
    if request.method=='POST':
        with transaction.atomic():
            services.audit(request.user,'Archivage' if hasattr(obj,'active') else 'Suppression',obj)
            if hasattr(obj,'active'):
                obj.active=False;obj.save(update_fields=['active']);messages.success(request,'Fiche archivée ; historique conservé.')
            else:
                try:
                    with transaction.atomic(): obj.delete()
                    messages.success(request,'Catégorie supprimée.')
                except ProtectedError: messages.error(request,'Cette catégorie est utilisée et ne peut pas être supprimée.')
        return redirect('entity_list',key=key)
    return render(request,'pharmacy/confirm.html',{'title':'Archiver / supprimer','object':obj,'back_url':reverse('entity_list',args=[key])})


@login_required
def entity_detail(request,key,pk):
    model,_,title,_=entity_config(key);services.require(request.user,'view_'+model._meta.model_name)
    obj=get_object_or_404(model,pk=pk)
    fields=[(f.verbose_name,f.value_from_object(obj)) for f in model._meta.fields if f.name not in ['id','photo']]
    ctx={'title':str(obj),'object':obj,'fields':fields,'key':key}
    if model is Medicine and request.user.has_perm('pharmacy.view_lot'): ctx['lots']=obj.lots.all()
    if model is Supplier and request.user.has_perm('pharmacy.view_purchase'): ctx['purchases']=Purchase.objects.filter(supplier=obj)
    if model is Customer and request.user.has_perm('pharmacy.view_sale'): ctx['sales']=Sale.objects.filter(customer=obj)
    return render(request,'pharmacy/detail.html',ctx)


@gate('view_purchase')
def purchase_list(request):
    query=Purchase.objects.select_related('supplier','author').prefetch_related('lines')
    if request.GET.get('q'): query=query.filter(supplier__name__icontains=request.GET['q'])
    if request.GET.get('status') in Purchase.Status.values: query=query.filter(status=request.GET['status'])
    return render(request,'pharmacy/purchases.html',{'title':"Commandes d'achat",'page_obj':page(request,query),'statuses':Purchase.Status.choices})


@gate('add_purchase')
def purchase_create(request):
    form=forms.PurchaseForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            obj=form.save(commit=False);obj.author=request.user;obj.save();services.audit(request.user,'Création achat',obj)
        return redirect('purchase_detail',pk=obj.pk)
    return render(request,'pharmacy/form.html',{'title':'Nouvelle commande','form':form})


@gate('view_purchase')
def purchase_detail(request,pk):
    obj=get_object_or_404(Purchase.objects.select_related('supplier').prefetch_related('lines__medicine','receipts'),pk=pk)
    form=forms.PurchaseLineForm(request.POST if request.method=='POST' and request.POST.get('action')=='add' else None)
    if request.method=='POST':
        try:
            action=request.POST.get('action')
            if action=='add':
                if form.is_valid(): services.add_purchase_line(request.user,obj.pk,**form.cleaned_data);return redirect('purchase_detail',pk=pk)
            elif action=='remove':
                line=request.POST.get('line','')
                if not line.isdigit(): raise ValidationError('Ligne invalide.')
                get_object_or_404(PurchaseLine,purchase=obj,pk=int(line))
                services.remove_purchase_line(request.user,pk,int(line));return redirect('purchase_detail',pk=pk)
            elif action in ['order','cancel']:
                services.order_purchase(request.user,pk,cancel=action=='cancel');messages.success(request,'Commande mise à jour.');return redirect('purchase_detail',pk=pk)
            else: raise ValidationError('Action inconnue.')
        except (ValidationError,OperationalError) as exc:error(request,exc)
    return render(request,'pharmacy/purchase_detail.html',{'title':str(obj),'object':obj,'form':form})


@gate('receive_purchase')
def purchase_receive(request,pk):
    obj=get_object_or_404(Purchase,pk=pk)
    form=forms.ReceiveForm(request.POST or None,purchase=obj,initial={'token':uuid.uuid4()})
    if request.method=='POST' and form.is_valid():
        d=form.cleaned_data
        try:
            services.receive_purchase(request.user,pk,[{'line_id':d['line'].pk,'quantity':d['quantity'],'number':d['number'],'expires_on':d['expires_on']}],d['token'])
            messages.success(request,'Réception enregistrée et stock augmenté.');return redirect('purchase_detail',pk=pk)
        except (ValidationError,OperationalError) as exc:error(request,exc)
    return render(request,'pharmacy/form.html',{'title':'Réceptionner '+str(obj),'form':form,'back_url':reverse('purchase_detail',args=[pk])})


@gate('view_sale')
def sale_list(request):
    query=Sale.objects.select_related('customer','author').prefetch_related('lines')
    start,end=period(request)
    query=query.filter(created_at__date__range=(start,end))
    if request.GET.get('q'): query=query.filter(Q(customer__name__icontains=request.GET['q'])|Q(author__username__icontains=request.GET['q']))
    return render(request,'pharmacy/sales.html',{'title':'Ventes & caisse','page_obj':page(request,query),'start':start,'end':end})


@gate('add_sale')
def sale_create(request):
    form=forms.SaleForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            obj=form.save(commit=False);obj.author=request.user;obj.save();services.audit(request.user,'Ouverture vente',obj)
        return redirect('sale_detail',pk=obj.pk)
    return render(request,'pharmacy/form.html',{'title':'Ouvrir une vente','form':form,'help':'Laissez le client vide pour une vente comptoir.'})


@gate('view_sale')
def sale_detail(request,pk):
    obj=get_object_or_404(Sale.objects.select_related('customer','author').prefetch_related('lines__lot__medicine','returns'),pk=pk)
    action=request.POST.get('action')
    cart=forms.CartForm(request.POST if request.method=='POST' and action=='add' else None)
    search=request.GET.get('q','').strip()
    if search and request.method=='GET':
        cart.fields['medicine'].queryset=cart.fields['medicine'].queryset.filter(Q(name__icontains=search)|Q(generic_name__icontains=search)|Q(barcode__iexact=search))
        match=cart.fields['medicine'].queryset.filter(barcode__iexact=search).first()
        if match: cart.initial.update(medicine=match.pk,quantity=1)
    checkout=forms.CheckoutForm(request.POST if request.method=='POST' and action=='validate' else None)
    if request.method=='POST':
        try:
            if action=='add' and cart.is_valid():
                d=cart.cleaned_data;services.add_sale_line(request.user,pk,d['medicine'],d['quantity'],d['lot'].pk if d['lot'] else None)
                return redirect('sale_detail',pk=pk)
            elif action=='remove':
                line=request.POST.get('line','')
                if not line.isdigit(): raise ValidationError('Ligne invalide.')
                get_object_or_404(SaleLine,sale=obj,pk=int(line))
                services.remove_sale_line(request.user,pk,int(line));return redirect('sale_detail',pk=pk)
            elif action=='validate' and checkout.is_valid():
                d=checkout.cleaned_data;d.pop('confirm')
                services.validate_sale(request.user,pk,**d);messages.success(request,'Vente validée, paiement enregistré et stock déduit.');return redirect('sale_detail',pk=pk)
            elif action not in ['add','validate']: raise ValidationError('Action inconnue.')
        except (ValidationError,OperationalError) as exc: error(request,exc)
    return render(request,'pharmacy/sale_detail.html',{'title':str(obj),'object':obj,'cart':cart,'checkout':checkout,'search':search})


@gate('return_sale')
def sale_return(request,pk):
    obj=get_object_or_404(Sale,pk=pk,status='validated')
    form=forms.ReturnForm(request.POST or None,sale=obj,initial={'token':uuid.uuid4()})
    if request.method=='POST' and form.is_valid():
        d=form.cleaned_data
        try:
            services.return_sale(request.user,d['line'].pk,d['quantity'],d['reason'],d['restock'],d['refund_reference'],d['token'])
            messages.success(request,'Retour et remboursement tracés.');return redirect('sale_detail',pk=pk)
        except (ValidationError,OperationalError) as exc: error(request,exc)
    return render(request,'pharmacy/form.html',{'title':'Retour — '+str(obj),'form':form})


@gate('view_lot')
def stock_list(request):
    today=timezone.localdate()
    query=Lot.objects.select_related('medicine')
    if request.GET.get('q'): query=query.filter(Q(medicine__name__icontains=request.GET['q'])|Q(number__icontains=request.GET['q'])|Q(medicine__barcode__icontains=request.GET['q']))
    status=request.GET.get('status')
    if status=='expired': query=query.filter(expires_on__lt=today,quantity__gt=0)
    elif status=='soon': query=query.filter(expires_on__range=(today,today+timedelta(days=90)),quantity__gt=0)
    elif status=='blocked': query=query.filter(blocked=True)
    elif status=='available': query=query.filter(blocked=False,expires_on__gte=today,quantity__gt=0)
    return render(request,'pharmacy/stock.html',{'title':'Stocks & lots','page_obj':page(request,query)})


@gate('adjust_stock')
def inventory(request,pk):
    obj=get_object_or_404(Lot,pk=pk)
    form=forms.InventoryForm(request.POST or None,initial={'counted':obj.quantity,'blocked':obj.blocked})
    if request.method=='POST' and form.is_valid():
        d=form.cleaned_data
        try:
            services.adjust_stock(request.user,pk,d['counted'],d['reason'],d['blocked']);messages.success(request,'Inventaire tracé.');return redirect('stock')
        except (ValidationError,OperationalError) as exc: error(request,exc)
    return render(request,'pharmacy/form.html',{'title':'Inventaire — '+str(obj),'form':form})


@gate('view_stockmovement')
def movements(request):
    query=StockMovement.objects.select_related('lot__medicine','author')
    if request.GET.get('q'): query=query.filter(Q(lot__medicine__name__icontains=request.GET['q'])|Q(lot__number__icontains=request.GET['q']))
    return render(request,'pharmacy/movements.html',{'title':'Mouvements de stock','page_obj':page(request,query)})


@gate('view_auditlog')
def audit_list(request):
    query=AuditLog.objects.select_related('author')
    if request.GET.get('q'):query=query.filter(Q(target__icontains=request.GET['q'])|Q(action__icontains=request.GET['q']))
    return render(request,'pharmacy/audit.html',{'title':"Journal d’audit",'page_obj':page(request,query)})


@gate('auth.view_user')
def users(request):
    return render(request,'pharmacy/users.html',{'title':'Utilisateurs & rôles','page_obj':page(request,User.objects.prefetch_related('groups').order_by('username'))})


@login_required
def user_edit(request,pk=None):
    if not request.user.has_perm('auth.change_user' if pk else 'auth.add_user'): raise PermissionDenied
    obj=get_object_or_404(User,pk=pk) if pk else None
    if obj and obj.is_superuser and not request.user.is_superuser: raise PermissionDenied
    form=(forms.AccountChangeForm if pk else forms.AccountCreateForm)(request.POST or None,instance=obj)
    if request.method=='POST' and form.is_valid():
        if obj and obj.pk==request.user.pk and not form.cleaned_data['is_active']:
            form.add_error('is_active','Vous ne pouvez pas désactiver votre propre compte.')
        else:
            with transaction.atomic():
                obj=form.save();services.audit(request.user,'Modification compte' if pk else 'Création compte',obj)
            messages.success(request,'Compte enregistré.');return redirect('users')
    return render(request,'pharmacy/form.html',{'title':'Modifier un compte' if pk else 'Créer un compte','form':form})


@login_required
def reports(request):
    start,end=period(request)
    return render(request,'pharmacy/reports.html',{'title':'Rapports & documents','start':start,'end':end})


@login_required
def document(request,kind,pk):
    from .pdf import document_response
    if kind in ['sale','invoice']:
        services.require(request.user,'view_sale');obj=get_object_or_404(Sale,pk=pk,status='validated')
        rows=[[str(l.lot.medicine),l.lot.number,l.quantity,l.unit_price,l.subtotal] for l in obj.lines.select_related('lot__medicine')]
        title=('Facture ' if kind=='invoice' else 'Reçu ')+str(obj)
        meta=[f'Client : {obj.customer or "Comptoir"}',f'Date : {timezone.localtime(obj.validated_at):%d/%m/%Y %H:%M}',f'Opérateur : {obj.author}',f'Paiement : {obj.payment.get_method_display()} · {obj.payment.reference}',f'Remboursements cumulés : {obj.refunded:,.2f} Ar']
        return document_response(title,['Médicament','Lot','Qté','P.U. (Ar)','Total (Ar)'],rows,obj.total,meta)
    if kind=='purchase':
        services.require(request.user,'view_purchase');obj=get_object_or_404(Purchase,pk=pk)
        rows=[[str(l.medicine),l.quantity,l.received,l.unit_price,l.subtotal] for l in obj.lines.select_related('medicine')]
        return document_response('Bon de commande '+str(obj),['Médicament','Qté','Reçu','P.U. (Ar)','Total (Ar)'],rows,obj.total,[f'Fournisseur : {obj.supplier}',f'Date : {obj.created_at:%d/%m/%Y}',f'Statut : {obj.get_status_display()}'])
    if kind=='receipt':
        services.require(request.user,'view_purchase');obj=get_object_or_404(Receipt,pk=pk)
        rows=[[str(l.lot.medicine),l.lot.number,l.quantity,l.unit_cost,l.quantity*l.unit_cost] for l in obj.lines.select_related('lot__medicine')]
        return document_response('Bon de réception '+str(obj),['Médicament','Lot','Qté','Coût (Ar)','Total (Ar)'],rows,obj.total,[f'Commande : {obj.purchase}',f'Date : {obj.created_at:%d/%m/%Y}',f'Auteur : {obj.author}'])
    raise Http404


@login_required
def report_pdf(request,kind):
    from .pdf import document_response
    start,end=period(request);meta=[f'Période : {start:%d/%m/%Y} au {end:%d/%m/%Y}']
    total=None
    if kind in ['stock','expiry']:
        services.require(request.user,'view_lot')
        query=Lot.objects.select_related('medicine')
        if kind=='expiry':query=query.filter(quantity__gt=0,expires_on__lte=timezone.localdate()+timedelta(days=90))
        rows=[[str(l.medicine),l.number,str(l.expires_on),l.quantity,'Bloqué' if l.blocked else 'Périmé' if l.expired else 'Disponible'] for l in query]
        headers=['Médicament','Lot','Péremption','Stock','État'];title='Stock par lot' if kind=='stock' else 'Lots périmés et à échéance sous 90 jours'
        meta=['Situation au '+str(timezone.localdate())]
    elif kind=='sales':
        services.require(request.user,'view_sale')
        query=Sale.objects.filter(status='validated',validated_at__date__range=(start,end)).prefetch_related('lines','returns')
        rows=[[str(s),str(timezone.localdate(s.validated_at)),s.total,s.refunded] for s in query]
        total=sum((s.total for s in query),Decimal('0'));headers=['Vente','Date','CA brut (Ar)','Retours cumulés (Ar)'];title='Rapport des ventes'
        refunds=SaleReturn.objects.filter(created_at__date__range=(start,end)).aggregate(n=Sum('amount'))['n'] or 0
        meta.append(f'Remboursements effectués pendant la période : {refunds:,.2f} Ar')
    elif kind=='purchases':
        services.require(request.user,'view_purchase')
        query=Receipt.objects.filter(created_at__date__range=(start,end)).select_related('purchase__supplier').prefetch_related('lines')
        rows=[[str(r),str(r.purchase.supplier),str(r.created_at.date()),r.total] for r in query]
        total=sum((r.total for r in query),Decimal('0'));headers=['Réception','Fournisseur','Date','Montant (Ar)'];title='Rapport des achats réceptionnés'
    else:raise Http404
    return document_response(title,headers,rows,total,meta)
