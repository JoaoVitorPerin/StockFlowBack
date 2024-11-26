from django.urls import path
from django.urls import include

urlpatterns = [
    path('user/', include('user.urls')),
    path('produto/', include('produto.urls')),
    path('cliente/', include('cliente.urls')),
]
