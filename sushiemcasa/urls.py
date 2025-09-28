

from django.urls import path
from . import views  
app_name = 'sushiemcasa'
urlpatterns = [
    
    path('', views.homepage, name='homepage'),
    path('contato/', views.pagina_contato, name='contato'),

    
    path('orders/', views.pagina_orders, name = 'orders'),
]