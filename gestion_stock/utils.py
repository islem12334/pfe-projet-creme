from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
from .models import Reception, SortieStockProduction, OuvertureProduction, LotReception


def lot_queryset(numero_lot):
    canonical = canonical_lot_identifier(numero_lot)
    if canonical:
        reception_id = int(canonical.split('-')[1])
        return Reception.objects.filter(pk=reception_id)

    reception_ids = LotReception.objects.filter(code=numero_lot).values_list('reception_id', flat=True)
    return Reception.objects.filter(pk__in=reception_ids)


def _parse_lot_identifier(lot_identifier):
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
    if lot_index < 1:
        return None
    return reception_id, lot_index


def lot_id_to_code(lot_identifier):
    parsed = _parse_lot_identifier(lot_identifier)
    if not parsed:
        return None

    reception_id, lot_index = parsed
    lot = LotReception.objects.filter(reception_id=reception_id, ordre=lot_index).first()
    return lot.code if lot else None


def canonical_lot_identifier(lot_identifier):
    parsed = _parse_lot_identifier(lot_identifier)
    if parsed:
        reception_id, lot_index = parsed
        lot = LotReception.objects.filter(reception_id=reception_id, ordre=lot_index).first()
        if not lot:
            return None
        return f"LOT-{reception_id}-{lot_index:02d}"

    if not lot_identifier:
        return None
    lot_code_value = lot_identifier.strip()
    lot = LotReception.objects.filter(code=lot_code_value).order_by('reception_id', 'ordre').first()
    if not lot:
        return None
    return f"LOT-{lot.reception_id}-{lot.ordre:02d}"


def lot_identifier_variants(lot_identifier):
    canonical = canonical_lot_identifier(lot_identifier)
    if not canonical:
        return []

    variants = [canonical]
    lot_code = lot_id_to_code(canonical)
    if lot_code:
        variants.append(lot_code)
    return list(dict.fromkeys(variants))


def lot_expiration_info(lot_identifier, reference_date=None):
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
    qs = LotReception.objects.select_related('reception').order_by('reception__id', 'ordre')
    if reference_date is not None:
        qs = qs.filter(reception__date_expiration__gte=reference_date)

    for lot in qs:
        canonical = f"LOT-{lot.reception_id}-{lot.ordre:02d}"
        yield {
            'lot_id': canonical,
            'date_expiration': lot.reception.date_expiration,
            'lot_code': lot.code,
        }


def available_lot_ids_for_sortie(reference_date=None):
    available = []
    for entry in _iter_reception_lot_entries(reference_date):
        canonical = entry['lot_id']
        stock_disponible = lot_total_received(canonical) - lot_total_sent_to_production(canonical)
        if stock_disponible > 0:
            available.append(canonical)
    return available


def available_lot_ids_for_production(reference_date=None):
    """Lots transférés vers la production (SortieStockProduction), tous disponibles pour ouverture."""
    from .models import SortieStockProduction as SSP
    return list(SSP.objects.exclude(numero_lot='').values_list('numero_lot', flat=True).distinct())


def available_lot_options_for_sortie(reference_date=None):
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
    """Options de lots disponibles pour ouverture (tous les lots transférés vers la production)."""
    from .models import SortieStockProduction as SSP
    from django.db.models import Sum
    base_date = reference_date or timezone.localdate()
    options = []
    for lot_id in SSP.objects.exclude(numero_lot='').values_list('numero_lot', flat=True).distinct():
        total_transferred = SSP.objects.filter(numero_lot=lot_id).aggregate(total=Sum('quantite'))['total'] or 0
        jours_restant = None
        date_expiration = None
        parsed = _parse_lot_identifier(lot_id)
        if parsed:
            from .models import Reception as Rec
            rec = Rec.objects.filter(pk=parsed[0]).first()
            if rec and rec.date_expiration:
                date_expiration = rec.date_expiration
                jours_restant = (rec.date_expiration - base_date).days
        options.append({
            'lot_id': lot_id,
            'date_expiration': date_expiration,
            'disponible': total_transferred,
            'jours_restant': jours_restant,
        })
    options.sort(key=lambda item: (item['date_expiration'] or timezone.localdate(), item['lot_id']))
    return options


def all_lot_options_for_sortie(reference_date=None):
    options = []
    base_date = reference_date or timezone.localdate()
    qs = LotReception.objects.select_related('reception').order_by('reception__date_expiration', 'reception__id', 'ordre')
    for lot in qs:
        lot_id = f"LOT-{lot.reception_id}-{lot.ordre:02d}"
        jours_restant = (lot.reception.date_expiration - base_date).days
        options.append({
            'lot_id': lot_id,
            'date_expiration': lot.reception.date_expiration,
            'disponible': 0,
            'jours_restant': jours_restant,
        })
    options.sort(key=lambda item: (item['date_expiration'], item['lot_id']))
    return options


def lot_exists(numero_lot):
    return lot_queryset(numero_lot).exists()


def lot_not_expired(numero_lot, reference_date):
    return lot_queryset(numero_lot).filter(date_expiration__gte=reference_date).exists()


def lot_total_received(numero_lot):
    canonical = canonical_lot_identifier(numero_lot)
    parsed = _parse_lot_identifier(canonical) if canonical else None
    if parsed:
        reception_id, lot_index = parsed
        lot = LotReception.objects.filter(reception_id=reception_id, ordre=lot_index).first()
        if lot:
            return lot.quantite
    return lot_queryset(numero_lot).aggregate(total=Sum('quantite'))['total'] or 0


def lot_total_sent_to_production(numero_lot):
    identifiers = lot_identifier_variants(numero_lot)
    if not identifiers:
        return 0
    return SortieStockProduction.objects.filter(numero_lot__in=identifiers).aggregate(total=Sum('quantite'))['total'] or 0


def lot_total_opened_in_production(numero_lot):
    identifiers = lot_identifier_variants(numero_lot)
    if not identifiers:
        return 0
    return OuvertureProduction.objects.filter(numero_lot__in=identifiers).aggregate(total=Sum('quantite'))['total'] or 0
