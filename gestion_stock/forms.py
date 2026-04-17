from django import forms
from django.utils import timezone
from .models import (
    Profile,
    OuvertureProduction,
    Reception,
    SortieStockProduction,
)
from .utils import *


class ReceptionForm(forms.ModelForm):
    nombre_lots = forms.ChoiceField(
        choices=[(i, f'{i} lot(s)') for i in range(1, 11)],
        label="Nombre de lots à réceptionner",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'quantite' in self.fields:
            self.fields['quantite'].required = False
            self.fields['quantite'].label = "Quantité totale (kg)"

        # Lot codes : not required
        for index in range(1, 11):
            field_name = f'lot_code{index}'
            if field_name in self.fields:
                self.fields[field_name].label = f"Code lot {index}"
                self.fields[field_name].required = False

        # Lot quantities : not required, default 0
        for index in range(1, 11):
            field_name = f'lot_quantite{index}'
            if field_name in self.fields:
                self.fields[field_name].required = False
                self.fields[field_name].initial = 0

        if 'fournisseur' in self.fields:
            self.fields['fournisseur'].required = True

    class Meta:
        model = Reception
        fields = [
            'fournisseur', 'date_expiration', 'quantite',
            'lot_code1',  'lot_code2',  'lot_code3',  'lot_code4',  'lot_code5',
            'lot_code6',  'lot_code7',  'lot_code8',  'lot_code9',  'lot_code10',
            'lot_quantite1',  'lot_quantite2',  'lot_quantite3',  'lot_quantite4',  'lot_quantite5',
            'lot_quantite6',  'lot_quantite7',  'lot_quantite8',  'lot_quantite9',  'lot_quantite10',
        ]
        widgets = {
            'date_expiration': forms.DateInput(attrs={'type': 'date', 'min': str(timezone.localdate())}),
            'quantite': forms.NumberInput(attrs={'step': '0.001', 'min': '0.001'}),
            'lot_code1':  forms.TextInput(attrs={'placeholder': 'Ex: LOT-001-01'}),
            'lot_code2':  forms.TextInput(attrs={'placeholder': 'Ex: LOT-001-02'}),
            'lot_code3':  forms.TextInput(attrs={'placeholder': 'Ex: LOT-001-03'}),
            'lot_code4':  forms.TextInput(attrs={'placeholder': 'Ex: LOT-001-04'}),
            'lot_code5':  forms.TextInput(attrs={'placeholder': 'Ex: LOT-001-05'}),
            'lot_code6':  forms.TextInput(attrs={'placeholder': 'Ex: LOT-001-06'}),
            'lot_code7':  forms.TextInput(attrs={'placeholder': 'Ex: LOT-001-07'}),
            'lot_code8':  forms.TextInput(attrs={'placeholder': 'Ex: LOT-001-08'}),
            'lot_code9':  forms.TextInput(attrs={'placeholder': 'Ex: LOT-001-09'}),
            'lot_code10': forms.TextInput(attrs={'placeholder': 'Ex: LOT-001-10'}),
            'lot_quantite1':  forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'lot_quantite2':  forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'lot_quantite3':  forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'lot_quantite4':  forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'lot_quantite5':  forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'lot_quantite6':  forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'lot_quantite7':  forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'lot_quantite8':  forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'lot_quantite9':  forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
            'lot_quantite10': forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
        }

    def clean_date_expiration(self):
        date_exp = self.cleaned_data.get('date_expiration')
        if date_exp and date_exp < timezone.localdate():
            raise forms.ValidationError("La date d'expiration ne peut pas être dans le passé.")
        return date_exp

    def clean(self):
        from decimal import Decimal
        cleaned_data = super().clean()
        nombre_lots = int(cleaned_data.get('nombre_lots', 0))

        # Validate declared lots: code + quantity required
        total = Decimal('0')
        for i in range(1, nombre_lots + 1):
            code_field = f'lot_code{i}'
            qty_field  = f'lot_quantite{i}'

            if not cleaned_data.get(code_field):
                self.add_error(code_field, f"Veuillez saisir le code du lot {i}.")

            qty = cleaned_data.get(qty_field) or Decimal('0')
            if qty <= 0:
                self.add_error(qty_field, f"La quantité du lot {i} doit être > 0.")
            else:
                total += qty

        # Force all lot_quantite to Decimal (no None allowed in DB)
        for i in range(1, 11):
            qty_field = f'lot_quantite{i}'
            val = cleaned_data.get(qty_field)
            if val is None or val == '' or (i > nombre_lots):
                cleaned_data[qty_field] = Decimal('0')

        # Auto-set total quantite = sum of per-lot quantities
        if total > 0:
            cleaned_data['quantite'] = total

        return cleaned_data


class ReceptionUpdateForm(forms.ModelForm):
    """Formulaire de modification d'une réception existante (sans contrainte date passée)."""

    class Meta:
        model = Reception
        fields = ['fournisseur', 'date_expiration', 'quantite',
                  'lot_code1', 'lot_code2', 'lot_code3', 'lot_code4', 'lot_code5',
                  'lot_code6', 'lot_code7', 'lot_code8', 'lot_code9', 'lot_code10']
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'date_expiration': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'step': '0.001', 'min': '0.001', 'class': 'form-control'}),
            'lot_code1':  forms.TextInput(attrs={'class': 'form-control'}),
            'lot_code2':  forms.TextInput(attrs={'class': 'form-control'}),
            'lot_code3':  forms.TextInput(attrs={'class': 'form-control'}),
            'lot_code4':  forms.TextInput(attrs={'class': 'form-control'}),
            'lot_code5':  forms.TextInput(attrs={'class': 'form-control'}),
            'lot_code6':  forms.TextInput(attrs={'class': 'form-control'}),
            'lot_code7':  forms.TextInput(attrs={'class': 'form-control'}),
            'lot_code8':  forms.TextInput(attrs={'class': 'form-control'}),
            'lot_code9':  forms.TextInput(attrs={'class': 'form-control'}),
            'lot_code10': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fournisseur'].required = True
        for i in range(1, 11):
            self.fields[f'lot_code{i}'].required = False
            self.fields[f'lot_code{i}'].label = f"Code lot {i}"
        self.fields['lot_code1'].required = True


class SortieStockProductionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Show all operators for selection
        self.fields['profile'].queryset = Profile.objects.filter(type_operateur__in=['magasin', 'production']).order_by('nom', 'prenom')
        self.fields['profile'].label = "Opérateur"
        self.fields['numero_lot'].label = "ID lot"
        self.fields['numero_lot'].help_text = "ID lot triés par date d'expiration (quantité disponible affichée)."
        self.fields['quantite'].label = "Quantité (kg)"
        self.fields['quantite'].help_text = "Valeur par défaut: 0,500 kg (500 g)."
        choices = [('', '--- Sélectionner un ID lot ---')] 
        for option in all_lot_options_for_sortie(timezone.localdate()):
            lot_id = option['lot_id']
            date_exp = option['date_expiration'].strftime('%d/%m/%Y')
            dispo = option['disponible']
            jours_restant = option.get('jours_restant')
            statut = ""
            if jours_restant is not None and jours_restant < 0:
                statut = " | ⛔ EXPIRÉ"
            elif jours_restant is not None and jours_restant <= 7:
                statut = f" | ⚠ EXP ≤7j ({jours_restant}j)"
            label = f"{lot_id} | Dispo: {dispo} | Exp: {date_exp}{statut}"
            choices.append((lot_id, label))
        self.fields['numero_lot'].widget = forms.Select(choices=choices)

        # Always show profile select, no auto-hide

    class Meta:
        model = SortieStockProduction
        fields = ['profile', 'numero_lot', 'quantite']

    def clean_numero_lot(self):
        lot_input = (self.cleaned_data.get('numero_lot') or '').strip()
        canonical = canonical_lot_identifier(lot_input)
        if not canonical:
            raise forms.ValidationError("ID lot invalide. Utilisez le format LOT-<id>-<nn>.")
        return canonical

    def clean(self):
        cleaned_data = super().clean()
        numero_lot = cleaned_data.get('numero_lot')
        quantite = cleaned_data.get('quantite') or 0

        if not numero_lot:
            return cleaned_data

        if not lot_exists(numero_lot):
            raise forms.ValidationError("Ce numéro de lot n'existe pas dans le stock reçu.")

        if not lot_not_expired(numero_lot, timezone.localdate()):
            raise forms.ValidationError("La date de consommation de ce lot est déjà atteinte.")

        disponible_stock = lot_total_received(numero_lot) - lot_total_sent_to_production(numero_lot)
        if quantite > disponible_stock:
            raise forms.ValidationError(
                f"Quantité insuffisante en stock principal pour le lot {numero_lot}. Disponible: {disponible_stock}."
            )

        return cleaned_data

class OuvertureProductionForm(forms.ModelForm):

    numero_lot = forms.ChoiceField(
        choices=[],
        required=False,
        label="Lot consommé"
    )

    class Meta:
        model = OuvertureProduction
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only production operators and add Bootstrap class
        self.fields['profile'].queryset = Profile.objects.filter(
            type_operateur='production'
        ).order_by('nom', 'prenom')
        self.fields['profile'].label = "Opérateur production"
        self.fields['profile'].widget.attrs.update({'class': 'form-select'})
        self.fields['quantite'] = forms.IntegerField(
            label="Quantité consommée (par pièces)",
            min_value=1,
            initial=1,
            widget=forms.NumberInput(attrs={
                'min': '1',
                'step': '1',
                'class': 'form-control',
                'placeholder': '1',
            })
        )
        self.fields['date_heure_ouverture'].label = "Date/Heure ouverture"
        self.fields['date_heure_ouverture'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'}
        )
        from django.db.models import Sum
        from .utils import _parse_lot_identifier
        base_date = timezone.localdate()
        choices = [('', '--- Sélectionner un lot transféré ---')]

        transferred_lots = SortieStockProduction.objects.values_list('numero_lot', flat=True).distinct()
        for lot_id in transferred_lots:
            if not lot_id: continue

            # Total transferred
            total_transferred = SortieStockProduction.objects.filter(numero_lot=lot_id).aggregate(Sum('quantite'))['quantite__sum'] or 0

            # Total used in production
            total_used = OuvertureProduction.objects.filter(numero_lot=lot_id).aggregate(Sum('quantite'))['quantite__sum'] or 0

            # Remaining
            remaining = total_transferred - total_used

            # Expiration: parse canonical ID (LOT-<id>-<nn>) to get reception by pk
            date_exp = "N/A"
            statut = ""
            parsed = _parse_lot_identifier(lot_id)
            if parsed:
                reception = Reception.objects.filter(pk=parsed[0]).first()
                if reception and reception.date_expiration:
                    date_exp = reception.date_expiration.strftime('%d/%m/%Y')
                    jours_restant = (reception.date_expiration - base_date).days
                    if jours_restant < 0:
                        statut = " | ⛔ EXPIRÉ"
                    elif jours_restant <= 7:
                        statut = f" | ⚠ EXP ≤7j ({jours_restant}j)"

            label = f"{lot_id} | Dispo: {remaining:.3f} kg | Exp: {date_exp}{statut}"
            choices.append((lot_id, label))
        
        self.fields['numero_lot'].choices = choices
        self.fields['numero_lot'].widget.attrs.update({
            'class': 'form-select',
            'style': 'max-width: 100%; width: 100%;',
        })
        # Bootstrap classes for remaining fields
        for fname in ['ligne_production', 'numero_ordre_fabrication', 'nom_produit']:
            if fname in self.fields:
                self.fields[fname].widget.attrs.update({'class': 'form-control'})
        if 'shift' in self.fields:
            self.fields['shift'].widget.attrs.update({'class': 'form-select'})
