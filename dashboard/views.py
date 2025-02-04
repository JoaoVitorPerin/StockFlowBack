from rest_framework.views import APIView
from django.http import JsonResponse
import service.dashboard.dashboard
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator

class EstoqueDashboardView(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def get(self, *args, **kwargs):
        marca_id = self.request.GET.get('marca_id')
        status, mensagem, estoque = service.dashboard.dashboard.DashboardEstoque().buscar_dados_estoque_geral(marca_id=marca_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'estoque': estoque})

class EstoqueMarcas(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def get(self, *args, **kwargs):
        status, mensagem, marcas = service.dashboard.dashboard.DashboardEstoque().buscar_dados_por_marcas()

        return JsonResponse({'status': status, 'mensagem': mensagem, 'marcas': marcas})