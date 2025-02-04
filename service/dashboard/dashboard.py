from produto.models import Estoque
from django.db.models import Count, Sum

class DashboardEstoque():
    def buscar_dados_estoque_geral(self, marca_id=None):
        try:
            if marca_id:
                dados_estoque = list(Estoque.objects.filter(produto_id__marca_id=marca_id).values(
                    "quantidade", "produto_id__nome", "produto_id__marca_id__nome", "produto_id__preco_venda", "produto_id__preco_compra", "produto_id__preco_compra_real"
                ))
                mensagem = "Dados do estoque por marca retornados com sucesso!"
            else:
                dados_estoque = list(Estoque.objects.all().values(
                    "quantidade", "produto_id__nome", "produto_id__marca_id__nome", "produto_id__preco_venda", "produto_id__preco_compra", "produto_id__preco_compra_real"
                ))
                mensagem = "Todos os dados do estoque retornados com sucesso!"

            estoque_formatado = [
                {
                    "nome_produto": item["produto_id__nome"].strip(),
                    "nome_marca": item["produto_id__marca_id__nome"].strip(),
                    "quantidade": item["quantidade"],
                    "compra_real": int(item["quantidade"]) * float(item["produto_id__preco_compra_real"]),
                    "preco_venda": int(item["quantidade"]) * float(item["produto_id__preco_venda"])
                }
                for item in dados_estoque
            ]

            return True, mensagem, estoque_formatado

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