from rest_framework.views import APIView
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator
import service.cotacao.cotacao
from django.http import JsonResponse
from datetime import datetime

class CotacaoCadastroView(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def get(self, *args, **kwargs):
        status, mensagem, cotacao = service.cotacao.cotacao.CotacaoSistema().lista_ultima_cotacao()

        return JsonResponse({'status': status, 'mensagem': mensagem, 'cotacao': cotacao})

    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def post(self, *args, **kwargs):
        cotacao = self.request.data.get('cotacao')
        data = datetime.now()
        status, mensagem, cotacao = service.cotacao.cotacao.CotacaoSistema().cadastrar_cotacao(cotacao=cotacao, data=data)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'cotacao': cotacao})