from django.urls import path
from django.urls import include

urlpatterns = [
    path('user/', include('user.urls')),
    path('produto/', include('produto.urls')),
    path('cliente/', include('cliente.urls')),
    path('pedido/', include('pedido.urls')),
    path('cotacao/', include('cotacao.urls')),
    path('marca/', include('marca.urls')),
    path('dashboard/', include('dashboard.urls')),
]
