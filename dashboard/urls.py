from django.urls import re_path, include
from dashboard.views import *

urlpatterns = [
    re_path(r'^estoque$', EstoqueDashboardView.as_view()),
    re_path(r'^marcas-estoque$', EstoqueMarcas.as_view()),
    re_path(r'^estoque/coeficiente-compra$', EstoqueCoeficienteCompra.as_view()),
    re_path(r'^vendas$', VendasDashboardView.as_view()),
    re_path(r'^atletas$', AtletasDashboardView.as_view()),
    re_path(r'^vendas-marcas$', VendasMarcasView.as_view())
]