"""Helpers de présentation uniquement : aucune requête ni mutation métier."""
from collections import OrderedDict
from decimal import Decimal, InvalidOperation
from django import template
from django.forms import CheckboxInput, CheckboxSelectMultiple, PasswordInput, Textarea, Select
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.html import format_html

register = template.Library()

class CashMedicineSelect(Select):
    """Prix indicatif sur l'option déjà rendue : pas de seconde liste de médicaments."""
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        medicine = getattr(value, 'instance', None)
        if medicine is not None:
            option['attrs']['data-price-minor'] = minor_units(medicine.sale_price)
        return option

@register.filter
def money(value):
    try:
        number = Decimal(str(value))
        if not number.is_finite(): return '—'
        return f'{number:,.2f}'.replace(',', '\u202f').replace('.', ',') + ' Ar'
    except (InvalidOperation, ValueError, TypeError):
        return '—'

@register.filter
def expiry_state(value):
    if not value: return ''
    days = (value - timezone.localdate()).days
    return 'expired' if days < 0 else 'soon' if days <= 90 else 'valid'

@register.simple_tag
def icon(name):
    return format_html('<svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-{}"></use></svg>', name)

@register.filter
def widget_kind(field):
    widget = field.field.widget
    if isinstance(widget, CheckboxSelectMultiple): return 'choices'
    if isinstance(widget, CheckboxInput): return 'checkbox'
    if isinstance(widget, PasswordInput): return 'password'
    return 'wide' if isinstance(widget, Textarea) else 'field'

@register.filter
def accessible_widget(field):
    attrs = {'class': 'form-control'}
    if isinstance(field.field.widget, CheckboxInput): attrs['class'] = 'form-check-input'
    descriptions = []
    if field.help_text or field_hint(field): descriptions.append(field.auto_id + '_help')
    descriptions.append(field.auto_id + '_feedback')
    if field.errors:
        descriptions.append(field.auto_id + '_errors')
        attrs['aria-invalid'] = 'true'
    if descriptions: attrs['aria-describedby'] = ' '.join(descriptions)
    if field.name == 'username': attrs['autocomplete'] = 'username'
    if field.name in ['password', 'old_password']: attrs['autocomplete'] = 'current-password'
    if field.name in ['password1','password2','new_password1','new_password2']: attrs['autocomplete'] = 'new-password'
    if field.name == 'quantity': attrs.update(inputmode='numeric', **{'data-quantity': ''})
    # Projeter les limites du modèle vers le widget, sans changer sa validation.
    model = getattr(getattr(field.form, '_meta', None), 'model', None)
    if getattr(field.field.widget, 'input_type', '') == 'number':
        attrs['inputmode'] = 'decimal' if getattr(field.field, 'decimal_places', None) is not None else 'numeric'
    if model and getattr(field.field.widget, 'input_type', '') == 'number':
        for validator in model._meta.get_field(field.name).validators:
            if isinstance(validator, (MinValueValidator, MaxValueValidator)) and not callable(validator.limit_value):
                limit = validator.limit_value
                attrs['min' if isinstance(validator, MinValueValidator) else 'max'] = format(limit, 'f') if isinstance(limit, Decimal) else str(limit)
    if field.name == 'photo':
        attrs.update({'accept': '.jpg,.jpeg,.png,.webp', 'data-max-bytes': str(5 * 1024 * 1024)})
        initial = getattr(field.value(), 'name', '')
        if initial: attrs['data-current-file'] = initial.rsplit('/', 1)[-1]
    widget = None
    if field.name == 'medicine' and 'lot' in field.form.fields and 'quantity' in field.form.fields:
        widget = CashMedicineSelect(attrs=field.field.widget.attrs.copy(), choices=field.field.widget.choices)
        widget.is_required = field.field.widget.is_required
    return field.as_widget(widget=widget, attrs=attrs)

@register.inclusion_tag('includes/form_fields.html')
def form_fields(form, wizard=False, operation=""):
    groups = OrderedDict()
    for field in form.visible_fields():
        if field.name in ['name','generic_name','category','form','dosage','manufacturer','barcode','photo']:
            group = 'Identification'
        elif field.name in ['purchase_price','sale_price','threshold']:
            group = 'Prix et seuil de stock'
        elif field.name in ['active','authorized','requires_prescription']:
            group = 'Disponibilité et délivrance'
        elif field.name in ['username','password','password1','password2','old_password','new_password1','new_password2','groups','is_active']:
            group = 'Accès au compte'
        elif field.name in ['first_name','last_name','phone','email','address','tax_id','contact']:
            group = 'Coordonnées'
        else: group = 'Détails de l’opération'
        groups.setdefault(group, []).append(field)
    layouts = {
        'receipt': [('Articles reçus', ['line', 'quantity']), ('Traçabilité du lot', ['number', 'expires_on']), ('Confirmation', ['confirm'])],
        'inventory': [('Comptage physique', ['counted', 'reason']), ('Disponibilité du lot', ['blocked']), ('Confirmation', ['confirm'])],
        'return': [('Article retourné', ['line', 'quantity', 'reason']), ('Remise en stock', ['restock']), ('Remboursement effectué', ['refund_reference']), ('Confirmation', ['confirm'])],
    }
    if operation in layouts:
        groups = OrderedDict((label, [form[name] for name in names if name in form.fields])
                             for label, names in layouts[operation])
    sections = list(groups.items())
    if wizard:
        sections = [(name if index < len(sections) - 1 else 'Contrôle et récapitulatif', fields)
                    for index, (name, fields) in enumerate(sections)]
    return {'form': form, 'groups': sections, 'wizard': wizard}

@register.inclusion_tag('includes/nav_item.html')
def nav_item(request, route, label, glyph, key=None):
    from django.urls import reverse
    current = request.resolver_match.url_name if request.resolver_match else ''
    families = {
        'purchases': ['purchases','purchase_create','purchase_detail','purchase_receive'],
        'sales': ['sales','sale_create','sale_detail','sale_return'],
        'stock': ['stock','inventory'],
        'users': ['users','user_create','user_edit'],
    }
    active = current in families.get(route,[route])
    if key:
        active = current.startswith('entity_') and request.resolver_match.kwargs.get('key') == key
    return {'url': reverse(route,args=[key] if key else []),'label':label,'glyph':glyph,'active':active}

@register.inclusion_tag('includes/filter_chips.html',takes_context=True)
def filter_chips(context):
    request=context['request'];chips=[]
    labels={'q':'Recherche','status':'État','sort':'Tri','category':'Catégorie'}
    values={'active':'Actifs','archived':'Archivés','available':'Disponibles','soon':'Sous 90 jours','expired':'Périmés','blocked':'Bloqués','name':'Nom A–Z','-name':'Nom Z–A','sale_price':'Prix croissant','-sale_price':'Prix décroissant','stock':'Stock croissant','draft':'Brouillon','ordered':'Commandée','partial':'Partiellement reçue','received':'Réceptionnée','cancelled':'Annulée'}
    for name,label in labels.items():
        value=request.GET.get(name)
        if value:
            params=request.GET.copy();params.pop(name,None);params.pop('page',None)
            display=values.get(value,value)
            if name=='category':
                for category in context.get('categories') or []:
                    if str(category.pk)==value: display=str(category);break
            chips.append({'label':label,'value':display,'url':'?'+params.urlencode()})
    return {'chips':chips,'reset_url':request.path}

@register.simple_tag(takes_context=True)
def operation_ui(context):
    route=context['request'].resolver_match.url_name
    options={
        'purchase_receive':('Enregistrer la réception','Le stock augmente uniquement des quantités effectivement reçues.'),
        'sale_return':('Confirmer le retour','Le remboursement doit déjà avoir été effectué. La remise en stock nécessite un contrôle du produit.'),
        'inventory':('Confirmer l’inventaire','La différence avec le stock actuel sera enregistrée dans les mouvements.'),
        'sale_create':('Ouvrir la caisse','Client facultatif : laissez ce champ vide pour une vente comptoir.'),
        'purchase_create':('Créer la commande','La commande reste en brouillon ; elle ne modifie pas le stock.'),
    }
    label,help_text=options.get(route,('Enregistrer','Les champs marqués « obligatoire » doivent être renseignés.'))
    kind = {'purchase_receive': 'receipt', 'inventory': 'inventory', 'sale_return': 'return'}.get(route, '')
    return {'label':label,'help':help_text,'kind':kind,'today':timezone.localdate().isoformat()}

@register.filter
def display_value(value):
    if isinstance(value, bool): return 'Oui' if value else 'Non'
    if isinstance(value, Decimal): return money(value)
    return value if value is not None else '—'

@register.filter
def subtract(value, other):
    return value - other


@register.filter
def field_hint(field):
    """Aide éditoriale ; aucune nouvelle règle de délivrance ou de paiement."""
    return {
        'barcode': 'Facultatif. Scannez ou saisissez le code ; son unicité sera vérifiée à l’enregistrement.',
        'photo': 'JPEG, PNG ou WebP, 5 Mo maximum. L’image sera contrôlée à l’enregistrement.',
        'purchase_price': 'Prix unitaire d’achat en ariary, strictement positif.',
        'sale_price': 'Prix unitaire de vente en ariary, strictement positif.',
        'threshold': 'Quantité minimale souhaitée. Une alerte apparaît lorsque le disponible atteint ce seuil.',
        'authorized': 'À cocher uniquement après contrôle de l’autorisation de délivrance.',
        'requires_prescription': 'L’ordonnance devra être contrôlée au moment de la vente.',
        'counted': 'Indiquez le nombre d’unités physiquement présentes, y compris zéro.',
        'refund_reference': 'Référence du remboursement déjà réalisé en dehors de PharmaGest.',
    }.get(field.name, '')


@register.filter
def minor_units(value):
    """Montant exact en centimes pour les aides UI ; jamais de flottant."""
    try:
        amount = Decimal(str(value))
        if not amount.is_finite(): return ''
        cents = amount * 100
        if cents != cents.to_integral_value(): return ''
        return str(int(cents))
    except (InvalidOperation, TypeError, ValueError):
        return ''
