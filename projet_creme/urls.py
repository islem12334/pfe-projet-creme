from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from gestion_stock import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('admin/', admin.site.urls),
    path('gestion_stock/', include('gestion_stock.urls')),
]

# Serve static files always (dev server)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
