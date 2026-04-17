from django.db import models
from django.db.models import Q, Sum
from decimal import Decimal
from django.contrib.auth.models import User

class Profile(models.Model):
    TYPE_CHOICES = [
        ('admin', 'Administrateur'),
        ('magasin', 'Magasinier'),
        ('production', 'Production'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricule = models.CharField(max_length=50, unique=True)
    type_operateur = models.CharField(max_length=20, choices=TYPE_CHOICES)

    nom = models.CharField(max_length=100, blank=True, default='')

    prenom = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"

    def save(self, *args, **kwargs):
        # Create User + strong password manually in /admin/auth/user/ first
        if self.user:
            self.user.username = self.matricule
        super().save(*args, **kwargs)

class Fournisseur(models.Model):
    nom = models.CharField(max_length=200)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return self.nom


class Reception(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='receptions')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    date_reception = models.DateTimeField(auto_now_add=True)

    lot_code1 = models.CharField(max_length=50)
    lot_code2 = models.CharField(max_length=50)
    lot_code3 = models.CharField(max_length=50)
    lot_code4 = models.CharField(max_length=50, blank=True, default='')
    lot_code5 = models.CharField(max_length=50, blank=True, default='')
    lot_code6 = models.CharField(max_length=50, blank=True, default='')
    lot_code7 = models.CharField(max_length=50, blank=True, default='')
    lot_code8 = models.CharField(max_length=50, blank=True, default='')
    lot_code9 = models.CharField(max_length=50, blank=True, default='')
    lot_code10 = models.CharField(max_length=50, blank=True, default='')

    # Quantité individuelle par lot (0 = non renseigné / ancien enregistrement)
    lot_quantite1  = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'))
    lot_quantite2  = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'))
    lot_quantite3  = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'))
    lot_quantite4  = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'))
    lot_quantite5  = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'))
    lot_quantite6  = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'))
    lot_quantite7  = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'))
    lot_quantite8  = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'))
    lot_quantite9  = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'))
    lot_quantite10 = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'))

    date_expiration = models.DateField()
    quantite = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.500'))

    def __str__(self):
        return f"Réception {self.id}"

    @property
    def lot_reference(self):
        return f"LOT-REC-{self.id}" if self.id else "LOT-REC-N/A"

    def lot_codes(self):
        return [
            self.lot_code1,
            self.lot_code2,
            self.lot_code3,
            self.lot_code4,
            self.lot_code5,
            self.lot_code6,
            self.lot_code7,
            self.lot_code8,
            self.lot_code9,
            self.lot_code10,
        ]


class SortieStockProduction(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='sorties')
    date_heure = models.DateTimeField(auto_now_add=True)
    numero_lot = models.CharField(max_length=50)
    quantite = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.500'))

    def __str__(self):
        return f"Sortie {self.numero_lot} ({self.quantite})"


class OuvertureProduction(models.Model):
    SHIFT_P1 = 'P1'
    SHIFT_P2 = 'P2'
    SHIFT_P3 = 'P3'
    SHIFT_CHOICES = [
        (SHIFT_P1, 'P1'),
        (SHIFT_P2, 'P2'),
        (SHIFT_P3, 'P3'),
    ]

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='ouvertures')
    ligne_production = models.CharField(max_length=100)
    date_heure_ouverture = models.DateTimeField()
    numero_lot = models.CharField(max_length=50)
    numero_ordre_fabrication = models.CharField(max_length=100)
    nom_produit = models.CharField(max_length=150)
    quantite = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.500'))
    shift = models.CharField(max_length=2, choices=SHIFT_CHOICES)

    def __str__(self):
        return f"Ouverture {self.numero_lot} - {self.nom_produit}"
