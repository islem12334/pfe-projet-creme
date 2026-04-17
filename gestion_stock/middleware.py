from django.shortcuts import redirect
from django.contrib import messages
from .models import Profile


class NoCacheAuthMiddleware:
    """
    Force le navigateur à ne jamais mettre en cache les pages authentifiées.
    Empêche l'accès via les boutons Précédent/Suivant après déconnexion.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.path.startswith('/gestion_stock/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response


class MagasinAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/gestion_stock/') and request.user.is_authenticated:
            # Block Django superuser from custom interfaces
            if request.user.is_superuser:
                return redirect('/admin/')

            try:
                profile_type = request.user.profile.type_operateur
            except Profile.DoesNotExist:
                messages.error(request, "Profil manquant - contactez admin")
                return redirect('login')

            # Production-only users blocked from magasin paths
            if request.path.startswith('/gestion_stock/production/'):
                if profile_type not in ['admin', 'production']:
                    return redirect('login')
            else:
                # Magasin paths: block production-only users
                if profile_type not in ['admin', 'magasin']:
                    return redirect('login')

        response = self.get_response(request)
        return response

