from django.http import JsonResponse
from rest_framework.views import APIView
import service.custo_mensal.custo_mensal as custo_service
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator

class CustoMensalView(APIView):
    @method_decorator(group_required('Administrador'))
    def get(self, *args, **kwargs):
        custo_id = self.request.GET.get('custo_id')

        status, mensagem, custos = custo_service.CustoMensalSistema().listar_custo_mensal(custo_id=custo_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'custos': custos})

    @method_decorator(group_required('Administrador'))
    def post(self, *args, **kwargs):
        data = self.request.data
        custo_id = data.get('custo_id')
        dat_ini = data.get('dat_ini')
        dat_fim = data.get('dat_fim')
        valor = data.get('valor')
        nome = data.get('nome')
        recorrente = data.get('recorrente')

        status, mensagem, custo_id = custo_service.CustoMensalSistema().cadastrar_custo_mensal(
            custo_id=custo_id,
            dat_ini=dat_ini,
            dat_fim=dat_fim,
            valor=valor,
            nome=nome,
            recorrente=recorrente
        )

        return JsonResponse({'status': status, 'descricao': mensagem, 'custo_id': custo_id})

    @method_decorator(group_required('Administrador'))
    def delete(self, *args, **kwargs):
        custo_id = self.request.GET.get('custo_id')

        status, mensagem = custo_service.CustoMensalSistema().excluir_custo_mensal(custo_id=custo_id)

        return JsonResponse({"mensagem": mensagem}, status=200)