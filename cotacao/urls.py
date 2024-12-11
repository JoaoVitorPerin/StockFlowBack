from django.urls import re_path, include
from cotacao.views import *

urlpatterns = [
    re_path(r'^cadastro$', CotacaoCadastroView.as_view()),
]