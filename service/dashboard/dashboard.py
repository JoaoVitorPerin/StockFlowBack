from produto.models import Estoque
from django.db.models import Sum
from django.db.models import F, Prefetch, Q
from django.utils.timezone import make_aware
from datetime import datetime
from pedido.models import Pedido, ItemPedido
from custo_mensal.models import CustoMensal

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


class DashboardVendas:
    @staticmethod
    def buscar_dados_vendas(anomes=None):
        try:
            mes = anomes[4:]
            ano = anomes[:4]

            # Definição dos limites de data
            data_inicio = make_aware(datetime(int(ano), int(mes), 1, 0, 0, 0))
            if int(mes) == 12:
                data_fim = make_aware(datetime(int(ano) + 1, 1, 1, 0, 0, 0))
            else:
                data_fim = make_aware(datetime(int(ano), int(mes) + 1, 1, 0, 0, 0))

            pedidos = Pedido.objects.filter(
                dataPedido__gte=data_inicio,
                dataPedido__lt=data_fim
            ).annotate(
                vlr_frete=F("frete"),
                nm_cliente=F("cliente_id__nome_completo"),
                is_atleta=F("cliente_id__is_atleta"),
                num_pedido=F("idPedido"),
                vlr_custo=Sum(F("itens__precoCusto") * F("itens__quantidade")),
                vlr_venda=Sum(F("itens__precoUnitario") * F("itens__quantidade")),
            ).prefetch_related(
                Prefetch('itempedido_set', queryset=ItemPedido.objects.all(), to_attr='itens')
            ).values(
                "dataPedido",
                "idPedido",
                "nm_cliente",
                "is_atleta",
                "vlr_frete",
                "vlr_custo",
                "vlr_venda"
            )

            total_venda = 0
            total_custo = 0
            total_lucro = 0
            total_frete = 0
            total_custo_atleta = 0
            qtd_pedidos_nao_atleta = 0
            pedidos_com_itens = []

            for pedido in pedidos:
                pedido_dict = dict(pedido)
                pedido_dict["vlr_custo"] = pedido["vlr_custo"] or 0
                pedido_dict["vlr_venda"] = (pedido["vlr_venda"] or 0) + pedido["vlr_frete"]
                pedido_dict["vlr_lucro"] = pedido_dict["vlr_venda"] - pedido_dict["vlr_custo"] - pedido_dict["vlr_frete"]

                if pedido_dict["vlr_venda"] - pedido_dict["vlr_frete"] != 0:
                    pedido_dict["vlr_margem"] = round(
                        (pedido_dict["vlr_lucro"] / (pedido_dict["vlr_venda"] - pedido_dict["vlr_frete"])) * 100, 2)
                else:
                    pedido_dict["vlr_margem"] = 0

                pedidos_com_itens.append(pedido_dict)

                total_venda += pedido_dict["vlr_venda"]
                total_frete += pedido_dict["vlr_frete"]
                total_custo += pedido_dict["vlr_custo"]
                total_lucro += pedido_dict["vlr_lucro"]

                if pedido["is_atleta"]:
                    total_custo_atleta += pedido_dict["vlr_custo"]
                else:
                    qtd_pedidos_nao_atleta += 1;

            total_custo_fixo = \
            CustoMensal.objects.filter(Q(anomes=anomes) | Q(recorrente=True)).aggregate(total=Sum("valor"))[
                "total"] or 0
            total_lucro -= total_custo_fixo

            dados_cards = {
                "vlr_total_venda": total_venda,
                "vlr_total_custo": total_custo - total_custo_atleta,
                "vlr_total_lucro": total_lucro,
                "vlr_total_frete": total_frete,
                "vlr_total_custo_atleta": total_custo_atleta,
                "vlr_total_custo_fixo": total_custo_fixo,
                "vlr_ticket_medio": round(total_venda / qtd_pedidos_nao_atleta, 2) if qtd_pedidos_nao_atleta > 0 else 0,
                "vlr_margem_liquida": round((total_lucro / total_venda) * 100, 2) if total_venda > 0 else 0
            }

            retorno = {
                "pedidos": pedidos_com_itens,
                "custos_mensais": list(CustoMensal.objects.filter(Q(anomes=anomes) | Q(recorrente=True)).values().order_by('id')),
                "cards": dados_cards
            }

            mensagem = f"Dados de vendas filtrados para {mes}/{ano} retornados com sucesso!"
            return True, mensagem, retorno

        except Exception as e:
            return False, f"Erro ao buscar dados de vendas: {str(e)}", []