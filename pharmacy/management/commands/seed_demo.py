import os, secrets, uuid
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from pharmacy.models import *
from pharmacy import services
from .setup_roles import setup_roles

class Command(BaseCommand):
    help='Ajoute un jeu fictif une seule fois ; aucun mot de passe par défaut.'
    @transaction.atomic
    def handle(self,*args,**options):
        setup_roles()
        if User.objects.filter(username='demo_admin').exists():
            self.stdout.write('Démonstration déjà initialisée ; aucune donnée modifiée.');return
        if Medicine.objects.exists():raise CommandError('La démonstration doit être chargée dans un catalogue vide.')
        password=os.environ.get('DEMO_PASSWORD') or secrets.token_urlsafe(14)
        user=User.objects.create_superuser('demo_admin','demo@example.test',password,first_name='Alice',last_name='Rakoto')
        supplier=Supplier.objects.create(name='Distribution Santé Démo',phone='020 00 000 00',address='Antananarivo — données fictives',contact='Équipe démo')
        supplier2=Supplier.objects.create(name='Médical Océan Démo',phone='020 00 000 01',email='contact@example.test')
        client=Customer.objects.create(name='Client de démonstration',phone='034 00 000 00')
        categories={n:Category.objects.create(name=n) for n in ['Antalgiques','Vitamines','Antiseptiques','Soins digestifs']}
        specs=[('Paracétamol','500 mg','Comprimé','Antalgiques','800','1500',60,10),('Vitamine C','1000 mg','Comprimé effervescent','Vitamines','2000','3500',35,10),('Chlorhexidine','0,05 %','Solution','Antiseptiques','2500','4200',8,10),('Ibuprofène','200 mg','Comprimé','Antalgiques','1400','2500',25,10),('Solution de réhydratation','','Sachet','Soins digestifs','600','1200',6,15),('Complexe multivitaminé','','Gélule','Vitamines','4500','6500',20,8),('Gel antiseptique','100 ml','Gel','Antiseptiques','1800','3000',45,12),('Vitamine D','1000 UI','Gélule','Vitamines','2200','3800',0,10)]
        p=Purchase.objects.create(supplier=supplier,author=user)
        medicines=[]
        for i,(name,dosage,form,cat,cost,price,qty,threshold) in enumerate(specs):
            med=Medicine.objects.create(name=name,generic_name=name,dosage=dosage,form=form,category=categories[cat],manufacturer='Laboratoire fictif',barcode=f'99000000000{i:02d}',purchase_price=Decimal(cost),sale_price=Decimal(price),threshold=threshold,authorized=True)
            medicines.append(med)
            if qty:services.add_purchase_line(user,p.pk,med,qty,Decimal(cost))
        services.order_purchase(user,p.pk)
        for i,line in enumerate(p.lines.all()):
            services.receive_purchase(user,p.pk,[{'line_id':line.pk,'quantity':line.quantity,'number':f'DEMO-{i+1:03d}','expires_on':timezone.localdate()+timedelta(days=35 if i in [1,2] else 365)}],uuid.uuid4())
        for idx,qty in [(0,3),(1,2),(3,1),(0,2)]:
            sale=Sale.objects.create(author=user,customer=client if idx==1 else None)
            services.add_sale_line(user,sale.pk,medicines[idx],qty)
            services.validate_sale(user,sale.pk)
        # Une réception ancienne devenue périmée illustre les alertes sans autoriser la vente.
        expired=Lot.objects.create(medicine=medicines[0],number='DEMO-PERIME',expires_on=timezone.localdate()-timedelta(days=5),quantity=4,received_quantity=4,unit_cost=Decimal('800'))
        StockMovement.objects.create(lot=expired,quantity=4,kind='inventory',reason='Stock initial fictif périmé',author=user)
        draft=Purchase.objects.create(supplier=supplier2,author=user)
        services.add_purchase_line(user,draft.pk,medicines[-1],30,Decimal('2200'))
        self.stdout.write(self.style.SUCCESS('Démonstration initialisée.'))
        self.stdout.write('Identifiant : demo_admin')
        self.stdout.write('Mot de passe : '+password)
