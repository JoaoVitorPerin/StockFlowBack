from produto.models import Estoque
from django.db.models import Count, Sum
from django.db.models import F

class DashboardEstoque():
    def buscar_dados_estoque_geral(self, marca_id=None, categoria_id=None):
        try:
            filtro = {}
            if marca_id:
                filtro["produto_id__marca_id"] = marca_id
            if categoria_id:
                filtro["produto_id__categoria_id"] = categoria_id

            dados_estoque = list(Estoque.objects.filter(**filtro).values(
                "quantidade",
                nome_produto=F("produto_id__nome"),
                nome_marca=F("produto_id__marca_id__nome"),
                nome_categoria=F("produto_id__categoria__nome"),
                preco_venda=F("produto_id__preco_venda"),
                preco_venda_multiplicado=F("produto_id__preco_venda") * F("quantidade"),
                compra_real=F("produto_id__preco_compra_real"),
                compra_real_multiplicado=F("produto_id__preco_compra_real") * F("quantidade")
            ))
            mensagem = "Dados do estoque filtrados retornados com sucesso!"

            return True, mensagem, dados_estoque

        except Exception as e:
            return False, str(e), []

    def buscar_dados_por_marcas(self):
        try:
            dados_estoque = Estoque.objects.values("produto_id__marca_id__nome").annotate(
                total_quantidade=Sum("quantidade")
            ).order_by("-total_quantidade")

            estoque_formatado = [
                {"marca": item["produto_id__marca_id__nome"], "quantidade_total": item["total_quantidade"]}
                for item in dados_estoque
            ]

            mensagem = "Dados de estoque por marca retornados com sucesso!"
            return True, mensagem, estoque_formatado

        except Exception as e:
            return False, str(e), []
