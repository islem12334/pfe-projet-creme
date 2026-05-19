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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantite'].required = False
        self.fields['fournisseur'].required = True

    class Meta:
        model = Reception
        fields = ['fournisseur', 'date_expiration', 'quantite']
        widgets = {
            'date_expiration': forms.DateInput(attrs={'type': 'date', 'min': str(timezone.localdate())}),
            'quantite': forms.NumberInput(attrs={'step': '0.001', 'min': '0.001'}),
        }

    def clean_date_expiration(self):
        date_exp = self.cleaned_data.get('date_expiration')
        if date_exp and date_exp < timezone.localdate():
            raise forms.ValidationError("La date d'expiration ne peut pas être dans le passé.")
        return date_exp


class ReceptionUpdateForm(forms.ModelForm):
    """Formulaire de modification d'une réception existante (sans contrainte date passée)."""

    class Meta:
        model = Reception
        fields = ['fournisseur', 'date_expiration', 'quantite']
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'date_expiration': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'step': '0.001', 'min': '0.001', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fournisseur'].required = True
        self.fields['quantite'].required = False


class SortieStockProductionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['profile'].queryset = Profile.objects.filter(type_operateur='magasin').order_by('nom', 'prenom')
        self.fields['profile'].label = "Opérateur magasin"
        self.fields['numero_lot'].label = "ID lot"
        self.fields['numero_lot'].help_text = "ID lot triés par date d'expiration (quantité disponible affichée)."
        self.fields['quantite'].label = "Quantité (kg)"
        self.fields['quantite'].help_text = "Valeur par défaut: 0,500 kg (500 g)."
        choices = [('', '--- Sélectionner un ID lot ---')]
        today = timezone.localdate()
        for option in all_lot_options_for_sortie(today):
            lot_id = option['lot_id']
            date_exp = option['date_expiration'].strftime('%d/%m/%Y')
            # Compute real disponible (lot_total_received uses per-lot quantite when set)
            dispo = lot_total_received(lot_id) - lot_total_sent_to_production(lot_id)
            jours_restant = option.get('jours_restant')
            statut = ""
            if jours_restant is not None and jours_restant < 0:
                statut = " | ⛔ EXPIRÉ"
            elif jours_restant is not None and jours_restant <= 7:
                statut = f" | ⚠ EXP ≤7j ({jours_restant}j)"
            label = f"{lot_id} | Dispo: {dispo:.3f} kg | Exp: {date_exp}{statut}"
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

class ProfileCreateForm(forms.Form):
    matricule = forms.CharField(
        max_length=50,
        label='Matricule',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: MAG-001'}),
    )
    nom = forms.CharField(
        max_length=100,
        label='Nom',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    prenom = forms.CharField(
        max_length=100,
        label='Prénom',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    type_operateur = forms.ChoiceField(
        choices=[],
        label='Type',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password_confirm = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, allowed_types=None, **kwargs):
        super().__init__(*args, **kwargs)
        if allowed_types is None:
            allowed_types = [c[0] for c in Profile.TYPE_CHOICES]
        self.fields['type_operateur'].choices = [
            c for c in Profile.TYPE_CHOICES if c[0] in allowed_types
        ]

    def clean_matricule(self):
        matricule = self.cleaned_data['matricule'].strip()
        if Profile.objects.filter(matricule=matricule).exists():
            raise forms.ValidationError("Ce matricule est déjà utilisé.")
        return matricule

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")
        return cleaned_data


class ProfileUpdateForm(forms.Form):
    matricule = forms.CharField(
        max_length=50,
        label='Matricule',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    nom = forms.CharField(
        max_length=100,
        label='Nom',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    prenom = forms.CharField(
        max_length=100,
        label='Prénom',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    type_operateur = forms.ChoiceField(
        choices=Profile.TYPE_CHOICES,
        label='Type',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    password = forms.CharField(
        required=False,
        label='Nouveau mot de passe',
        help_text='Laisser vide pour ne pas changer.',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Laisser vide pour garder le même'}),
    )
    password_confirm = forms.CharField(
        required=False,
        label='Confirmer le nouveau mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, instance=None, allowed_types=None, **kwargs):
        self.instance = instance
        if instance and not args and 'data' not in kwargs:
            kwargs.setdefault('initial', {})
            kwargs['initial'].setdefault('matricule', instance.matricule)
            kwargs['initial'].setdefault('nom', instance.nom)
            kwargs['initial'].setdefault('prenom', instance.prenom)
            kwargs['initial'].setdefault('type_operateur', instance.type_operateur)
        super().__init__(*args, **kwargs)
        if allowed_types:
            self.fields['type_operateur'].choices = [
                c for c in Profile.TYPE_CHOICES if c[0] in allowed_types
            ]

    def clean_matricule(self):
        matricule = self.cleaned_data['matricule'].strip()
        qs = Profile.objects.filter(matricule=matricule)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce matricule est déjà utilisé par un autre profil.")
        return matricule

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")
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
            label="Quantité OF (pièces)",
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

        # Lots already consumed in a previous ouverture → exclude them
        already_used = set(
            OuvertureProduction.objects.exclude(numero_lot='')
            .values_list('numero_lot', flat=True)
        )
        # When editing, the current record's lot must always remain visible
        current_lot = (
            self.instance.numero_lot
            if self.instance and self.instance.pk and self.instance.numero_lot
            else None
        )

        transferred_lots = SortieStockProduction.objects.values_list('numero_lot', flat=True).distinct()
        for lot_id in transferred_lots:
            if not lot_id: continue
            # Skip used lots, but always keep the lot of the record being edited
            if lot_id in already_used and lot_id != current_lot:
                continue

            # Total transferred to production (kg)
            total_transferred = SortieStockProduction.objects.filter(
                numero_lot=lot_id
            ).aggregate(Sum('quantite'))['quantite__sum'] or 0

            # Expiration info
            date_exp = "N/A"
            jours_restant = None
            parsed = _parse_lot_identifier(lot_id)
            if parsed:
                reception = Reception.objects.filter(pk=parsed[0]).first()
                if reception and reception.date_expiration:
                    date_exp = reception.date_expiration.strftime('%d/%m/%Y')
                    jours_restant = (reception.date_expiration - base_date).days

            # Skip expired lots
            if jours_restant is not None and jours_restant < 0:
                continue

            statut = ""
            if jours_restant is not None and jours_restant <= 7:
                statut = f" | ⚠ EXP ≤7j ({jours_restant}j)"

            label = f"{lot_id} | Transféré: {total_transferred:.3f} kg | Exp: {date_exp}{statut}"
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

    def clean_numero_ordre_fabrication(self):
        of = self.cleaned_data.get('numero_ordre_fabrication', '').strip()
        qs = OuvertureProduction.objects.filter(numero_ordre_fabrication=of)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"L'OF « {of} » existe déjà. Chaque ordre de fabrication doit être unique.")
        return of
