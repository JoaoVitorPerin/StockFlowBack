from django.urls import re_path, include
from cliente.views import *

urlpatterns = [
    re_path(r'^cadastro$', ClienteCadastoView.as_view()),
]