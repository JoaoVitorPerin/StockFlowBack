from django.http import JsonResponse
from rest_framework.views import APIView
import service.custo_mensal.custo_mensal as custo_service
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator

class CustoMensalView(APIView):
    @method_decorator(group_required('Administrador'))
    def get(self, *args, **kwargs):
        custo_id = self.request.GET.get('custo_id')
        anomes = self.request.GET.getlist('anomes')
        status, mensagem, custos = custo_service.CustoMensalSistema().listar_custo_mensal(custo_id=custo_id, anomes=anomes)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'custos': custos})

    @method_decorator(group_required('Administrador'))
    def post(self, *args, **kwargs):
        data = self.request.data
        custo_id = data.get('custo_id')
        anomes = data.get('anomes')
        valor = data.get('valor')
        nome = data.get('nome')
        recorrente = data.get('recorrente')

        status, mensagem, custo_id = custo_service.CustoMensalSistema().cadastrar_custo_mensal(
            custo_id=custo_id,
            anomes=anomes,
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