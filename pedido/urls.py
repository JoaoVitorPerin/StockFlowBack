from django.urls import re_path, include
from pedido.views import *

urlpatterns = [
    re_path(r'^cadastro$', PedidoCadastroView.as_view()),
]