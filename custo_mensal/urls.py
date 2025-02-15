from django.urls import re_path, include
from custo_mensal.views import *

urlpatterns = [
    re_path(r'^cadastro$', CustoMensalView.as_view()),
]