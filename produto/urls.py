from django.urls import re_path, include
from produto.views import ProdutoCadastoView

urlpatterns = [
    re_path(r'^cadastro$', ProdutoCadastoView.as_view()),
]