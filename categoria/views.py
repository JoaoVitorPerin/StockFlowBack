from rest_framework.views import APIView
from django.http import JsonResponse
import service.categoria.categoria
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny, IsAuthenticated

class CategoriaCadastroView(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def get(self, *args, **kwargs):
        categoria_id = self.request.GET.get('categoria_id')
        status, mensagem, categorias = service.categoria.categoria.CategoriasSistema().lista_categorias(categoria_id=categoria_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'categorias': categorias})

    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def post(self, *args, **kwargs):
        categoria_id = self.request.data.get('categoria_id')
        nome = self.request.data.get('nome')

        status, mensagem, categoria_id = service.categoria.categoria.CategoriasSistema().cadastrar_categoria(
                                                                                        categoria_id=categoria_id,
                                                                                        nome=nome
                                                                                        )

        return JsonResponse({'status': status, 'descricao':mensagem, 'categoria_id': categoria_id})