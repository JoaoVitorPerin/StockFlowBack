from django.urls import re_path, include
from categoria.views import *

urlpatterns = [
    re_path(r'^cadastro$', CategoriaCadastroView.as_view())
]