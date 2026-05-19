from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    path('', views.production, name='index'),
    path('data_performance/', views.data_performance, name='data_performance'),
    path('profile/', views.profile_production, name='profile'),
    path('profile/add/', views.profile_production_add, name='profile_add'),
    path('profile/<int:pk>/', views.profile_production_detail, name='profile_detail'),
    path('profile/<int:pk>/modifier/', views.profile_production_update, name='profile_update'),
    path('stock/', views.stock_actuel_production, name='stock'),
    path('historique/', views.historique, name='historique'),
    path('historique/<int:pk>/', views.ouverture_detail, name='ouverture_detail'),
    path('historique/<int:pk>/modifier/', views.ouverture_update, name='ouverture_update'),
    path('historique/<int:pk>/supprimer/', views.ouverture_delete, name='ouverture_delete'),
    path('nouvelle/', views.nouvelle_production, name='nouvelle_production'),
    path('ouverture/new/', views.OuvertureProductionCreateView.as_view(), name='new'),
    path('ouverture/list/', views.OuvertureProductionListView.as_view(), name='list'),
]
