from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
from .models import Reception, SortieStockProduction, OuvertureProduction


def lot_queryset(numero_lot):
    """
    Retourne le queryset des réceptions correspondant au numéro de lot.
    """
    canonical = canonical_lot_identifier(numero_lot)
    if canonical:
        reception_id = int(canonical.split('-')[1])
        return Reception.objects.filter(pk=reception_id)

    query = Q(lot_code1=numero_lot) | Q(lot_code2=numero_lot) | Q(lot_code3=numero_lot)
    for index in range(4, 11):
        query |= Q(**{f'lot_code{index}': numero_lot})
    return Reception.objects.filter(query)


def _parse_lot_identifier(lot_identifier):
    """
    Parse un identifiant de lot au format LOT-<id>-<nn>.
    Retourne (reception_id, lot_index) ou None.
    """
    if not lot_identifier:
        return None
    value = lot_identifier.strip().upper()
    parts = value.split('-')
    if len(parts) != 3:
        return None
    if parts[0] != 'LOT' or not parts[1].isdigit() or not parts[2].isdigit():
        return None

    reception_id = int(parts[1])
    lot_index = int(parts[2])
    if lot_index < 1 or lot_index > 10:
        return None
    return reception_id, lot_index


def lot_id_to_code(lot_identifier):
    """
    Convertit un identifiant canonique LOT-<id>-<nn> en code lot réel.
    """
    parsed = _parse_lot_identifier(lot_identifier)
    if not parsed:
        return None

    reception_id, lot_index = parsed
    reception = Reception.objects.filter(pk=reception_id).first()
    if not reception:
        return None

    lot_code = getattr(reception, f'lot_code{lot_index}', '')
    return lot_code if lot_code else None


def canonical_lot_identifier(lot_identifier):
    """
    Convertit n'importe quel identifiant (code lot ou canonique) en format standard LOT-<id>-<nn>.
    """
    parsed = _parse_lot_identifier(lot_identifier)
    if parsed:
        reception_id, lot_index = parsed
        reception = Reception.objects.filter(pk=reception_id).first()
        if not reception:
            return None
        lot_code = getattr(reception, f'lot_code{lot_index}', '')
        if not lot_code:
            return None
        return f"LOT-{reception_id}-{lot_index:02d}"

    if not lot_identifier:
        return None
    lot_code_value = lot_identifier.strip()
    query = Q(lot_code1=lot_code_value) | Q(lot_code2=lot_code_value) | Q(lot_code3=lot_code_value)
    for index in range(4, 11):
        query |= Q(**{f'lot_code{index}': lot_code_value})

    reception = Reception.objects.filter(query).order_by('id').first()
    if not reception:
        return None

    for lot_index in range(1, 11):
        if getattr(reception, f'lot_code{lot_index}') == lot_code_value:
            return f"LOT-{reception.id}-{lot_index:02d}"
    return None


def lot_identifier_variants(lot_identifier):
    """
    Retourne toutes les variantes valides d'un identifiant de lot.
    """
    canonical = canonical_lot_identifier(lot_identifier)
    if not canonical:
        return []

    variants = [canonical]
    lot_code = lot_id_to_code(canonical)
    if lot_code:
        variants.append(lot_code)
    return list(dict.fromkeys(variants))


def lot_expiration_info(lot_identifier, reference_date=None):
    """
    Informations d'expiration pour un lot.
    """
    canonical = canonical_lot_identifier(lot_identifier)
    if not canonical:
        return {
            'date_expiration': None,
            'jours_restant': None,
            'status': 'unknown',
            'label': 'Inconnu',
        }

    parsed = _parse_lot_identifier(canonical)
    if not parsed:
        return {
            'date_expiration': None,
            'jours_restant': None,
            'status': 'unknown',
            'label': 'Inconnu',
        }

    reception_id, _ = parsed
    reception = Reception.objects.filter(pk=reception_id).first()
    if not reception:
        return {
            'date_expiration': None,
            'jours_restant': None,
            'status': 'unknown',
            'label': 'Inconnu',
        }

    if reference_date is None:
        reference_date = timezone.localdate()

    jours_restant = (reception.date_expiration - reference_date).days
    if jours_restant < 0:
        status = 'expired'
        label = '⛔ Expiré'
    elif jours_restant <= 7:
        status = 'warning'
        label = f'⚠ ≤7j ({jours_restant}j)'
    else:
        status = 'ok'
        label = f'✅ OK ({jours_restant}j)'

    return {
        'date_expiration': reception.date_expiration,
        'jours_restant': jours_restant,
        'status': status,
        'label': label,
    }


def _iter_reception_lot_entries(reference_date=None):
    """
    Générateur pour itérer sur tous les lots des réceptions.
    """
    queryset = Reception.objects.all().order_by('id')
    if reference_date is not None:
        queryset = queryset.filter(date_expiration__gte=reference_date)

    for reception in queryset:
        for lot_index in range(1, 11):
            lot_code = getattr(reception, f'lot_code{lot_index}', '')
            if lot_code:
                canonical = f"LOT-{reception.id}-{lot_index:02d}"
                yield {
                    'lot_id': canonical,
                    'date_expiration': reception.date_expiration,
                    'lot_code': lot_code,
                }


def available_lot_ids_for_sortie(reference_date=None):
    """
    IDs des lots disponibles pour sortie (stock principal > 0).
    """
    available = []
    for entry in _iter_reception_lot_entries(reference_date):
        canonical = entry['lot_id']
        stock_disponible = lot_total_received(canonical) - lot_total_sent_to_production(canonical)
        if stock_disponible > 0:
            available.append(canonical)
    return available


def available_lot_ids_for_production(reference_date=None):
    """
    IDs des lots disponibles pour production (frigo production > 0).
    """
    available = []
    for entry in _iter_reception_lot_entries(reference_date):
        canonical = entry['lot_id']
        stock_disponible = lot_total_sent_to_production(canonical) - lot_total_opened_in_production(canonical)
        if stock_disponible > 0:
            available.append(canonical)
    return available


def available_lot_options_for_sortie(reference_date=None):
    """
    Options lots pour formulaire sortie (dispo > 0).
    """
    options = []
    base_date = reference_date or timezone.localdate()
    for entry in _iter_reception_lot_entries(reference_date):
        lot_id = entry['lot_id']
        disponible = lot_total_received(lot_id) - lot_total_sent_to_production(lot_id)
        if disponible > 0:
            jours_restant = (entry['date_expiration'] - base_date).days
            options.append({
                'lot_id': lot_id,
                'date_expiration': entry['date_expiration'],
                'disponible': disponible,
                'jours_restant': jours_restant,
            })

    options.sort(key=lambda item: (item['date_expiration'], item['lot_id']))
    return options


def available_lot_options_for_production(reference_date=None):
    """
    Options lots pour formulaire production (frigo > 0).
    """
    options = []
    base_date = reference_date or timezone.localdate()
    for entry in _iter_reception_lot_entries(reference_date):
        lot_id = entry['lot_id']
        disponible = lot_total_sent_to_production(lot_id) - lot_total_opened_in_production(lot_id)
        if disponible > 0:
            jours_restant = (entry['date_expiration'] - base_date).days
            options.append({
                'lot_id': lot_id,
                'date_expiration': entry['date_expiration'],
                'disponible': disponible,
                'jours_restant': jours_restant,
            })

    options.sort(key=lambda item: (item['date_expiration'], item['lot_id']))
    return options


def all_lot_options_for_sortie(reference_date=None):
    """
    TOUS les lots pour formulaire sortie (même dispo=0), triés par expiration.
    Direct loop over Reception lot_code1-10 without filtering.
    """
    from .models import Reception
    from django.utils import timezone
    options = []
    base_date = reference_date or timezone.localdate()
    receptions = Reception.objects.all().order_by('date_expiration')
    for reception in receptions:
        for lot_index in range(1, 11):
            lot_code = getattr(reception, f'lot_code{lot_index}', '')
            if lot_code.strip():
                lot_id = f"LOT-{reception.id}-{lot_index:02d}"
                jours_restant = (reception.date_expiration - base_date).days
                disponible = 0  # Show all, compute if needed
                options.append({
                    'lot_id': lot_id,
                    'date_expiration': reception.date_expiration,
                    'disponible': disponible,
                    'jours_restant': jours_restant,
                })
    
    options.sort(key=lambda item: (item['date_expiration'], item['lot_id']))
    return options


def lot_exists(numero_lot):
    """
    Vérifie si le lot existe en réception.
    """
    return lot_queryset(numero_lot).exists()


def lot_not_expired(numero_lot, reference_date):
    """
    Vérifie si le lot n'est pas expiré.
    """
    return lot_queryset(numero_lot).filter(date_expiration__gte=reference_date).exists()


def lot_total_received(numero_lot):
    """
    Quantité réceptionnée pour le lot individuel.
    Utilise lot_quantite{i} si renseigné, sinon divise le total équitablement.
    """
    canonical = canonical_lot_identifier(numero_lot)
    parsed = _parse_lot_identifier(canonical) if canonical else None
    if parsed:
        reception_id, lot_index = parsed
        reception = Reception.objects.filter(pk=reception_id).first()
        if reception:
            per_lot_qty = getattr(reception, f'lot_quantite{lot_index}', 0) or 0
            if per_lot_qty > 0:
                return per_lot_qty
            # Fallback pour anciens enregistrements : diviser le total équitablement
            lot_count = sum(
                1 for i in range(1, 11)
                if getattr(reception, f'lot_code{i}', '').strip()
            )
            if lot_count > 0:
                return (reception.quantite or 0) / lot_count
    return lot_queryset(numero_lot).aggregate(total=Sum('quantite'))['total'] or 0


def lot_total_sent_to_production(numero_lot):
    """
    Quantité totale envoyée en production pour le lot.
    """
    identifiers = lot_identifier_variants(numero_lot)
    if not identifiers:
        return 0
    return SortieStockProduction.objects.filter(numero_lot__in=identifiers).aggregate(total=Sum('quantite'))['total'] or 0


def lot_total_opened_in_production(numero_lot):
    """
    Quantité totale ouverte en production pour le lot.
    """
    identifiers = lot_identifier_variants(numero_lot)
    if not identifiers:
        return 0
    return OuvertureProduction.objects.filter(numero_lot__in=identifiers).aggregate(total=Sum('quantite'))['total'] or 0

