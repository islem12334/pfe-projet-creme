from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.views import View
from django.utils.functional import cached_property
from .models import Profile

class PermissionMixin(LoginRequiredMixin, View):
    """
    Base mixin for operator permissions using Profile.role.
    """
    def has_permission(self):
        # Block superuser from magasin
        if self.request.user.is_superuser:
            return False
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            return False
        return profile.type_operateur in ['admin', 'magasin']

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return HttpResponseForbidden("Accès refusé.")
        return super().dispatch(request, *args, **kwargs)

class MagasinAccessMixin(PermissionMixin):
    """Require Administrateur or Magasinier access."""
    pass

class AdminRequiredMixin(PermissionMixin):
    """Require Administrateur access only (modify/delete)."""
    def has_permission(self):
        if self.request.user.is_superuser:
            return False
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            return False
        return profile.type_operateur == 'admin'

class ProductionAccessMixin(LoginRequiredMixin, View):
    """Require Administrateur or Production access."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.type_operateur not in ['admin', 'production']:
            from django.shortcuts import redirect
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class OperateurRequiredMixin(LoginRequiredMixin):
    """Require any logged-in user with profile."""
    pass

class AdminOrOperateurMixin(PermissionMixin):
    """Admin or operateur (all logged-in)."""
    def has_permission(self):
        return self.request.user.is_authenticated

