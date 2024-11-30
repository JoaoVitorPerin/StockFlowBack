from django.http import JsonResponse
from rest_framework.views import APIView

import service.pedido.pedido
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny, IsAuthenticated

class PedidoCadastroView(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def get(self, *args, **kwargs):
        pedido_id = self.request.GET.get('pedido_id')
        status, mensagem, pedidos = service.pedido.pedido.PedidoSistema().listar_pedidos(pedido_id=pedido_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'pedidos': pedidos})

    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def post(self, *args, **kwargs):
        pedido_id = self.request.data.get('pedido_id')
        data_pedido = self.request.data.get('data_pedido')
        cliente_id = self.request.data.get('cliente_id')
        itens = self.request.data.get('itens')
        desconto = self.request.data.get('desconto', 0.0)

        status, mensagem, pedido_id = service.pedido.pedido.PedidoSistema().cadastrar_pedido(
            pedido_id=pedido_id,
            data_pedido=data_pedido,
            cliente_id=cliente_id,
            itens=itens,
            desconto=desconto
        )

        return JsonResponse({'status': status, 'descricao':mensagem, 'pedido_id': pedido_id})

    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def delete(self, *args, **kwargs):
        pedido_id = self.request.GET.get('pedido_id')

        status, mensagem = service.pedido.pedido.PedidoSistema().deletar_pedido(pedido_id=pedido_id)

        return JsonResponse({"mensagem": mensagem}, status=200)