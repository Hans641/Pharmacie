from django.conf import settings
def brand(request):
    return {'pharmacy_name': settings.PHARMACY_NAME}
