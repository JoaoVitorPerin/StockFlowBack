from django.http import JsonResponse
from rest_framework.views import APIView
from datetime import datetime
import service.pedido.pedido
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny, IsAuthenticated

class PedidoCadastroView(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque', 'Operador de Pedidos'))
    def get(self, *args, **kwargs):
        pedido_id = self.request.GET.get('pedido_id')
        status, mensagem, pedidos = service.pedido.pedido.PedidoSistema().listar_pedidos(pedido_id=pedido_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'pedidos': pedidos})

    @method_decorator(group_required('Administrador', 'Operador de Estoque', 'Operador de Pedidos'))
    def post(self, *args, **kwargs):
        data = self.request.data
        pedido_id = data.get('pedido_id')
        data_pedido = datetime.now()
        cliente_id = data.get('cliente_id')
        itens = data.get('itens')
        desconto = data.get('desconto', 0.0)
        frete = data.get('frete', 0.0)
        vlr_total = data.get('total', 0.0)
        usuario_id = data.get('usuario_id')

        # Novos campos de endereço
        logradouro = data.get('logradouro')
        numero = data.get('numero')
        complemento = data.get('complemento')
        bairro = data.get('bairro')
        localidade = data.get('localidade')
        uf = data.get('uf')
        cep = data.get('cep')

        status, mensagem, pedido_id = service.pedido.pedido.PedidoSistema().cadastrar_pedido(
            pedido_id=pedido_id,
            data_pedido=data_pedido,
            cliente_id=cliente_id,
            itens=itens,
            desconto=desconto,
            frete=frete,
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            localidade=localidade,
            uf=uf,
            usuario_id=usuario_id,
            cep=cep,
            vlr_total = vlr_total
        )

        return JsonResponse({'status': status, 'descricao': mensagem, 'pedido_id': pedido_id})

    @method_decorator(group_required('Administrador', 'Operador de Estoque', 'Operador de Pedidos'))
    def delete(self, *args, **kwargs):
        pedido_id = self.request.GET.get('pedido_id')

        status, mensagem = service.pedido.pedido.PedidoSistema().deletar_pedido(pedido_id=pedido_id)

        return JsonResponse({"mensagem": mensagem}, status=200)

class PedidoStatusView(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque', 'Operador de Pedidos'))
    def post(self, *args, **kwargs):
        data = self.request.data
        pedido_id = data.get('pedido_id')

        status, mensagem = service.pedido.pedido.PedidoSistema().alterar_status_pedido(pedidos=pedido_id)
        return JsonResponse({'status': status, 'mensagem': mensagem})