from django.urls import re_path, include
from marca.views import *

urlpatterns = [
    re_path(r'^cadastro$', MarcaCadastroView.as_view())
]