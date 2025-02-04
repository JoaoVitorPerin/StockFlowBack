from django.urls import re_path, include
from dashboard.views import EstoqueDashboardView, EstoqueMarcas

urlpatterns = [
    re_path(r'^estoque$', EstoqueDashboardView.as_view()),
    re_path(r'^marcas-estoque$', EstoqueMarcas.as_view())
]