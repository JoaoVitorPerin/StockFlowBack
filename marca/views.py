from rest_framework.views import APIView
from django.http import JsonResponse
import service.marca.marca
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny, IsAuthenticated

class MarcaCadastroView(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def get(self, *args, **kwargs):
        marca_id = self.request.GET.get('marca_id')
        status, mensagem, marcas = service.marca.marca.MarcaSistema().listar_marcas(marca_id=marca_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'marcas': marcas})

    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def post(self, *args, **kwargs):
        marca_id = self.request.data.get('marca_id')
        nome = self.request.data.get('nome')

        status, mensagem, marca_id = service.marca.marca.MarcaSistema().cadastrar_marca(
                                                                                        marca_id=marca_id,
                                                                                        nome=nome
                                                                                    )

        return JsonResponse({'status': status, 'descricao':mensagem, 'marca_id': marca_id})