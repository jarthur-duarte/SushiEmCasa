from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('orders/', views.pagina_orders, name = 'orders'),
]