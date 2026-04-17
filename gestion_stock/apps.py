from django.apps import AppConfig

class GestionStockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_stock'

    def ready(self):
        import gestion_stock.signals

