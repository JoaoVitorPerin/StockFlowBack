from custo_mensal.models import CustoMensal
from django.db.models import Q

class CustoMensalSistema():
    def listar_custo_mensal(self, custo_id=None):
        try:
            if custo_id:
                custo = CustoMensal.objects.values().filter(id=custo_id).first()
                lista_custo = custo
            else:
                lista_custo = list(CustoMensal.objects.all().values().order_by('id'))
            return True, 'Custos mensais retornados com sucesso', lista_custo
        except Exception as e:
            return False, str(e), []

    def cadastrar_custo_mensal(self, custo_id=None, nome=None, valor=None, dat_ini=None, dat_fim=None, recorrente=None):
        try:
            if not custo_id :
                novo_custo = CustoMensal(
                    nome=nome,
                    valor=valor,
                    dat_ini=dat_ini,
                    dat_fim=dat_fim,
                    recorrente=recorrente
                )
                novo_custo.save()

                return True, 'Custo mensal cadastrado com sucesso!', novo_custo.id

            else:
                custo_mensal = CustoMensal.objects.filter(id=custo_id).first()
                if not custo_mensal:
                    return False, 'Custo mensal não encontrado!', None

                custo_mensal.nome = nome
                custo_mensal.valor = valor
                custo_mensal.dat_ini = dat_ini
                custo_mensal.dat_fim = dat_fim
                custo_mensal.recorrente = recorrente
                custo_mensal.save()

                return True, 'Custo mensal atualizado com sucesso!', custo_mensal.id

        except Exception as e:
            return False, str(e), None

    def excluir_custo_mensal(self, custo_id=None):
        try:
            custo_mensal = CustoMensal.objects.filter(id=int(custo_id)).first()

            if custo_mensal:
                custo_mensal.delete()
                return True, 'Custo mensal deletado com sucesso!'
            else:
                return False, 'Custo mensal não encontrado'
        except Exception as e:
            return False, str(e), None