from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('production/', include('gestion_stock.urls_production', namespace='production')),
    path('magasin/', views.dashboard, name='dashboard'),
    path('reception/', views.reception_list, name='reception_list'),
    path('reception/new/', views.ReceptionCreateView.as_view(), name='reception_new'),
    path('transfert/', views.transfert_create, name='transfert'),
    path('transfert/list/', views.transfert_list, name='transfert_list'),
    path('stock/', views.stock_actuel, name='stock'),
    path('profile/', views.profile_list, name='profile'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('reception/<int:pk>/', views.reception_detail, name='reception_detail'),
    path('reception/<int:pk>/update/', views.ReceptionUpdateView.as_view(), name='reception_update'),
    path('reception/<int:pk>/delete/', views.reception_delete, name='reception_delete'),
    path('transfert/<int:pk>/', views.transfert_detail, name='transfert_detail'),
    path('transfert/<int:pk>/update/', views.transfert_update, name='transfert_update'),
    path('transfert/<int:pk>/delete/', views.transfert_delete, name='transfert_delete'),
]

