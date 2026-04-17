from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    path('', views.production, name='index'),
    path('data_performance/', views.data_performance, name='data_performance'),
    path('profile/', views.profile_production, name='profile'),
    path('stock/', views.stock_actuel_production, name='stock'),
    path('historique/', views.historique, name='historique'),
    path('historique/<int:pk>/', views.ouverture_detail, name='ouverture_detail'),
    path('historique/<int:pk>/modifier/', views.ouverture_update, name='ouverture_update'),
    path('historique/<int:pk>/supprimer/', views.ouverture_delete, name='ouverture_delete'),
    path('nouvelle/', views.nouvelle_production, name='nouvelle_production'),
    path('ouverture/new/', views.OuvertureProductionCreateView.as_view(), name='new'),
    path('ouverture/list/', views.OuvertureProductionListView.as_view(), name='list'),
]
