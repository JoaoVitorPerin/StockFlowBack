from rest_framework.views import APIView
from django.http import JsonResponse
import service.dashboard.dashboard
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator

class EstoqueDashboardView(APIView):
    @method_decorator(group_required('Administrador'))
    def get(self, *args, **kwargs):
        marca_id = self.request.GET.get('marca_id')
        categoria_id= self.request.GET.get('categoria_id')
        status, mensagem, estoque = service.dashboard.dashboard.DashboardEstoque().buscar_dados_estoque_geral(marca_id=marca_id, categoria_id=categoria_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'estoque': estoque})

class EstoqueMarcas(APIView):
    @method_decorator(group_required('Administrador'))
    def get(self, *args, **kwargs):
        status, mensagem, marcas = service.dashboard.dashboard.DashboardEstoque().buscar_dados_por_marcas()

        return JsonResponse({'status': status, 'mensagem': mensagem, 'marcas': marcas})

class VendasDashboardView(APIView):
    @method_decorator(group_required('Administrador'))
    def get(self, *args, **kwargs):
        anomes = self.request.GET.get('anomes')
        status, mensagem, vendas = service.dashboard.dashboard.DashboardVendas.buscar_dados_vendas(anomes=anomes)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'vendas': vendas})

class AtletasDashboardView(APIView):
    @method_decorator(group_required('Administrador'))
    def get(self, *args, **kwargs):
        atleta_id = self.request.GET.get('atleta_id')
        anomes = self.request.GET.get('anomes')
        status, mensagem, atletas = service.dashboard.dashboard.DashboardAtletas().buscar_dados_atletas(anomes=anomes, atleta_id=atleta_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'atletas': atletas})

class VendasMarcasView(APIView):
    @method_decorator(group_required('Administrador'))
    def get(self, *args, **kwargs):
        anomes = self.request.GET.get('anomes')
        marca_id = self.request.GET.get('marca_id')
        status, mensagem, dados_vendas_marcas = service.dashboard.dashboard.DashboardVendasMarca().buscar_dados_vendas_marcas(marca_id=marca_id, anomes=anomes)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'dados_vendas_marcas': dados_vendas_marcas})