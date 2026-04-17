# Updated for Django User + Profile

def role_flags(request):
    is_admin = False
    profile = None
    try:
        profile = getattr(request.user, 'profile', None)
        if profile:
            # Safe access to avoid column errors
            type_operateur = getattr(profile, 'type_operateur', None) or getattr(profile, 'role', None)
            is_admin = type_operateur == 'admin'
    except Exception:
        profile = None
        is_admin = False
    
    return {
        'nav_show_reception': request.user.is_authenticated,
        'nav_show_sortie_stock': request.user.is_authenticated,
        'nav_show_ouverture_production': request.user.is_authenticated,
        'nav_show_stock': request.user.is_authenticated,
        'nav_show_history': request.user.is_authenticated,
        'nav_show_analytics': request.user.is_authenticated,
        'nav_is_admin': is_admin,
        'show_reception': request.user.is_authenticated,
        'show_sortie_stock': request.user.is_authenticated,
        'show_ouverture_production': request.user.is_authenticated,
        'show_stock': request.user.is_authenticated,
        'show_history': request.user.is_authenticated,
        'show_analytics': request.user.is_authenticated,
    }
