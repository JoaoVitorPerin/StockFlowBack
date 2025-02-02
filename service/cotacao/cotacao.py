from cotacao.models import Cotacao
from produto.models import Produto
from django.forms.models import model_to_dict
from decimal import Decimal

class CotacaoSistema():
    def lista_ultima_cotacao(self):
        try:
            ultima_cotacao = Cotacao.objects.order_by('-id').first()

            if ultima_cotacao:
                cotacao_dict = model_to_dict(ultima_cotacao)
                return True, 'Ultima cotacao retornada com sucesso', cotacao_dict
        except Exception as e:
            return False, str(e), None

    def cadastrar_cotacao(self, cotacao=None, data=None):
        try:
            if cotacao:
                nova_cotacao = Cotacao(
                    valor = cotacao,
                    data = data
                )

                nova_cotacao.save()

                produtos = Produto.objects.all()

                #atualizar todos os produtos de acordo com a cotacao
                for produto in produtos:
                    produto.preco_compra_real = (float(produto.preco_compra) * float(cotacao)) * 1.25
                    produto.save()

                return True, 'Cadastro realizado', nova_cotacao.id
        except Exception as e:
            return False, str(e), None
