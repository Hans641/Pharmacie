from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path, include
from pharmacy import views as v
urlpatterns=[
 path('admin/',admin.site.urls),
 path('comptes/',include('django.contrib.auth.urls')),
 path('',v.dashboard,name='dashboard'),
 path('catalogue/<str:key>/',v.entity_list,name='entity_list'),
 path('catalogue/<str:key>/ajouter/',v.entity_edit,name='entity_create'),
 path('catalogue/<str:key>/<int:pk>/',v.entity_detail,name='entity_detail'),
 path('catalogue/<str:key>/<int:pk>/modifier/',v.entity_edit,name='entity_edit'),
 path('catalogue/<str:key>/<int:pk>/archiver/',v.entity_delete,name='entity_delete'),
 path('achats/',v.purchase_list,name='purchases'),path('achats/nouveau/',v.purchase_create,name='purchase_create'),
 path('achats/<int:pk>/',v.purchase_detail,name='purchase_detail'),path('achats/<int:pk>/reception/',v.purchase_receive,name='purchase_receive'),
 path('ventes/',v.sale_list,name='sales'),path('ventes/nouvelle/',v.sale_create,name='sale_create'),
 path('ventes/<int:pk>/',v.sale_detail,name='sale_detail'),path('ventes/<int:pk>/retour/',v.sale_return,name='sale_return'),
 path('stocks/',v.stock_list,name='stock'),path('stocks/<int:pk>/inventaire/',v.inventory,name='inventory'),
 path('mouvements/',v.movements,name='movements'),path('audit/',v.audit_list,name='audit'),
 path('utilisateurs/',v.users,name='users'),path('utilisateurs/ajouter/',v.user_edit,name='user_create'),path('utilisateurs/<int:pk>/',v.user_edit,name='user_edit'),
 path('rapports/',v.reports,name='reports'),path('rapports/<str:kind>.pdf',v.report_pdf,name='report_pdf'),path('documents/<str:kind>/<int:pk>.pdf',v.document,name='document'),
]
# Les photos restent réservées aux utilisateurs du catalogue, même en développement.
from django.contrib.auth.decorators import login_required, permission_required
from django.views.static import serve
urlpatterns += [path('media/<path:path>',login_required(permission_required('pharmacy.view_medicine',raise_exception=True)(serve)),{'document_root':settings.MEDIA_ROOT})]
