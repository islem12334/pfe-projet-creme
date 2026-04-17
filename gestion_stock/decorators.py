import functools
from django.shortcuts import redirect, resolve_url
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Profile

def magasin_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            next_url = request.GET.get('next', 'login')
            return redirect(next_url)

        # Block superuser (admin Django)
        if request.user.is_superuser:
            messages.error(request, "Admin Django n'a pas accès à cette interface")
            next_url = request.GET.get('next', '/admin/')
            return redirect(next_url)

        try:
            profile = request.user.profile
            if profile.type_operateur not in ['admin', 'magasin']:
                messages.error(request, "Accès refusé")
                next_url = request.GET.get('next', 'login')
                return redirect(next_url)
        except Profile.DoesNotExist:
            messages.error(request, "Profil manquant")
            next_url = request.GET.get('next', 'login')
            return redirect(next_url)

        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            next_url = request.GET.get('next', 'login')
            return redirect(next_url)

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        try:
            profile = request.user.profile
            if profile.type_operateur != 'admin':
                return HttpResponseForbidden("Accès réservé aux administrateurs")
        except Profile.DoesNotExist:
            return HttpResponseForbidden("Profil manquant")

        return view_func(request, *args, **kwargs)
    return wrapper


def production_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not hasattr(request.user, 'profile'):
            return redirect('login')

        if request.user.profile.type_operateur not in ['production', 'admin']:
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return wrapper

