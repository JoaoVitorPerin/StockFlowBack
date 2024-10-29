from django.urls import re_path, include
from produto.views import ProdutoCadastoView, ProdutoEstoqueView

urlpatterns = [
    re_path(r'^cadastro$', ProdutoCadastoView.as_view()),
    re_path(r'estoque$', ProdutoEstoqueView.as_view())
]