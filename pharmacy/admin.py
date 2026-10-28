from django.contrib import admin
from .models import *

admin.site.site_header='PharmaGest — Administration'
admin.site.site_title='PharmaGest'

class ReadOnlyAdmin(admin.ModelAdmin):
    list_per_page=30
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display=['name','category','dosage','sale_price','active','authorized']
    search_fields=['name','barcode','generic_name']
    list_filter=['active','category']
    def has_delete_permission(self,request,obj=None): return False
    def save_model(self,request,obj,form,change):
        super().save_model(request,obj,form,change)
        from .services import audit
        audit(request.user,'Modification catalogue via administration',obj)

for model in [Category,Supplier,Customer]: admin.site.register(model)
for model in [Purchase,PurchaseLine,Lot,Receipt,ReceiptLine,Sale,SaleLine,Payment,SaleReturn,StockMovement,AuditLog]: admin.site.register(model,ReadOnlyAdmin)
