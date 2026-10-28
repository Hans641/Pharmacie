from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

ROLE_PERMISSIONS={
 'Pharmacien responsable': {
  'medicine':['view','add','change','delete'], 'category':['view','add','change','delete'],
  'supplier':['view'], 'customer':['view','add','change'], 'purchase':['view','add','change','receive'],
  'lot':['view','adjust_stock'], 'sale':['view','add','change','validate','return','verify_payment'],
  'stockmovement':['view'],'auditlog':['view'],
 },
 'Gestionnaire de stock':{
  'medicine':['view','add','change'], 'category':['view','add','change'],
  'supplier':['view','add','change','delete'], 'purchase':['view','add','change','receive'],
  'lot':['view','adjust_stock'],'stockmovement':['view'],
 },
 'Caissier':{'medicine':['view'],'category':['view'],'customer':['view','add','change'],'lot':['view'],'sale':['view','add','change','validate']},
 'Responsable de gestion':{'medicine':['view'],'category':['view'],'supplier':['view'],'purchase':['view'],'lot':['view'],'sale':['view'],'stockmovement':['view'],'auditlog':['view']},
}

def setup_roles():
    result=[]
    for name,mapping in ROLE_PERMISSIONS.items():
        codes=[]
        for model,actions in mapping.items():
            for action in actions:
                codes.append(action if action in ['adjust_stock'] else f'{action}_{model}')
        group,_=Group.objects.get_or_create(name=name)
        group.permissions.set(Permission.objects.filter(content_type__app_label='pharmacy',codename__in=codes));result.append(group)
    group,_=Group.objects.get_or_create(name='Administrateur')
    group.permissions.set(Permission.objects.filter(content_type__app_label='pharmacy')|Permission.objects.filter(content_type__app_label='auth',codename__in=['view_user','add_user','change_user','view_group']))
    result.append(group)
    return result

class Command(BaseCommand):
    help='Crée ou remet à jour les cinq rôles métier (permissions cumulables).'
    def handle(self,*args,**options):
        for group in setup_roles(): self.stdout.write(self.style.SUCCESS(str(group)))
