from django.contrib import admin
from .models import Profile, Fournisseur, Reception, SortieStockProduction, OuvertureProduction

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['matricule', 'nom', 'prenom', 'type_operateur']
    list_filter = ['type_operateur']
    raw_id_fields = ('user',)
    search_fields = ['matricule', 'nom', 'prenom', 'user__username']
    fields = ('user', 'matricule', 'type_operateur', 'nom', 'prenom')

admin.site.register(Fournisseur)
admin.site.register(Reception)
admin.site.register(SortieStockProduction)
admin.site.register(OuvertureProduction)
