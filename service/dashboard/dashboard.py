from produto.models import Estoque
from django.db.models import Sum
from collections import defaultdict
from django.db.models import F, Prefetch, Q
from django.utils.timezone import make_aware
from datetime import datetime
from pedido.models import Pedido, ItemPedido
from cliente.models import Cliente
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

            dados_cards = {
                "vlr_total_venda": sum(item["preco_venda_multiplicado"] for item in dados_estoque),
                "vlr_total_compra": sum(item["compra_real_multiplicado"] for item in dados_estoque),
                "vlr_diferenca": sum(item["preco_venda_multiplicado"] for item in dados_estoque) - sum(item["compra_real_multiplicado"] for item in dados_estoque)
            }

            dict_estoque = {
                "tabela": dados_estoque,
                "cards": dados_cards
            }
            mensagem = "Dados do estoque filtrados retornados com sucesso!"

            return True, mensagem, dict_estoque

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
                vlr_total=F("vlrTotal"),
                vlr_custo=Sum(F("itens__precoCusto") * F("itens__quantidade")),
            ).prefetch_related(
                Prefetch('itempedido_set', queryset=ItemPedido.objects.all(), to_attr='itens')
            ).values(
                "dataPedido",
                "idPedido",
                "nm_cliente",
                "is_atleta",
                "vlr_frete",
                "vlr_custo",
                "vlr_total"
            ).order_by("-dataPedido")

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
                pedido_dict["vlr_lucro"] = pedido_dict["vlr_total"] - pedido_dict["vlr_custo"] - pedido_dict["vlr_frete"]

                if pedido_dict["vlr_total"] - pedido_dict["vlr_frete"] != 0:
                    pedido_dict["vlr_margem"] = round(
                        (pedido_dict["vlr_lucro"] / (pedido_dict["vlr_total"] - pedido_dict["vlr_frete"])) * 100, 2)
                else:
                    pedido_dict["vlr_margem"] = 0

                pedidos_com_itens.append(pedido_dict)

                total_venda += pedido_dict["vlr_total"]
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

class DashboardAtletas():
    def buscar_dados_atletas(self, anomes=None, atleta_id=None):
        try:
            mes = anomes[4:]
            ano = anomes[:4]

            data_inicio = make_aware(datetime(int(ano), int(mes), 1, 0, 0, 0))
            if int(mes) == 12:
                data_fim = make_aware(datetime(int(ano) + 1, 1, 1, 0, 0, 0))
            else:
                data_fim = make_aware(datetime(int(ano), int(mes) + 1, 1, 0, 0, 0))

            if(atleta_id):
                filtro_pedidos = {
                    "dataPedido__gte": data_inicio,
                    "dataPedido__lt": data_fim
                }

                filtro_pedidos["cliente_id__indicacao_id"] = atleta_id

                pedidos = Pedido.objects.filter(**filtro_pedidos).annotate(
                    vlr_frete=F("frete"),
                    nm_cliente=F("cliente_id__nome_completo"),
                    num_pedido=F("idPedido"),
                    vlr_total=F("vlrTotal"),
                    vlr_custo=Sum(F("itens__precoCusto") * F("itens__quantidade")),
                ).prefetch_related(
                    Prefetch('itempedido_set', queryset=ItemPedido.objects.all(), to_attr='itens')
                ).values(
                    "dataPedido",
                    "idPedido",
                    "nm_cliente",
                    "vlr_frete",
                    "vlr_custo",
                    "vlr_total"
                ).order_by("-dataPedido")

                pedidos_com_itens = []

                for pedido in pedidos:
                    pedido_dict = dict(pedido)

                    pedido_dict["vlr_custo"] = pedido["vlr_custo"] or 0

                    pedido_dict["vlr_lucro"] = pedido_dict["vlr_total"] - pedido_dict["vlr_custo"] - pedido_dict[
                        "vlr_frete"]

                    if pedido_dict["vlr_total"] - pedido_dict["vlr_frete"] != 0:
                        pedido_dict["vlr_margem"] = round(
                            (pedido_dict["vlr_lucro"] / (pedido_dict["vlr_total"] - pedido_dict["vlr_frete"])) * 100, 2
                        )
                    else:
                        pedido_dict["vlr_margem"] = 0

                    pedidos_com_itens.append(pedido_dict)

                return True, "Pedidos retornados com sucesso", pedidos_com_itens
            else:
                pedidos = Pedido.objects.filter(
                    dataPedido__gte=data_inicio,
                    dataPedido__lt=data_fim
                ).annotate(
                    vlr_frete=F("frete"),
                    nm_cliente=F("cliente_id__nome_completo"),
                    id_indicacao=F("cliente_id__indicacao_id"),
                    nm_indicacao=F("cliente_id__indicacao_id__nome_completo"),
                    is_atleta=F("cliente_id__is_atleta"),
                    num_pedido=F("idPedido"),
                    vlr_total=F("vlrTotal"),
                    vlr_custo=Sum(F("itens__precoCusto") * F("itens__quantidade")),
                ).prefetch_related(
                    Prefetch('itempedido_set', queryset=ItemPedido.objects.all(), to_attr='itens')
                ).values(
                    "idPedido",
                    "dataPedido",
                    "nm_cliente",
                    "id_indicacao",
                    "nm_indicacao",
                    "is_atleta",
                    "vlr_frete",
                    "vlr_custo",
                    "vlr_total",
                    "cliente_id"
                ).order_by("-dataPedido")

                atletas = Cliente.objects.filter(is_atleta=True).values("id", "nome_completo")
                atletas_dict = {atleta["id"]: atleta["nome_completo"] for atleta in atletas}

                indicacoes_agrupadas = defaultdict(lambda: {
                    "id_indicacao": 0,
                    "nm_indicacao": "",
                    "vlr_total_lucro_pedidos": 0,
                    "vlr_total": 0,
                    "qtd_indicacao": 0,
                    "vlr_custo": 0,  # Soma do valor total dos pedidos relacionados
                })

                for pedido in pedidos:
                    id_indicacao = pedido["id_indicacao"] or pedido[
                        "cliente_id"]  # Se não houver indicacao_id, usa cliente_id

                    if id_indicacao not in atletas_dict:
                        continue  # Ignorar se não for atleta

                    nm_indicacao = atletas_dict[id_indicacao]

                    vlr_custo = pedido["vlr_custo"] or 0
                    vlr_frete = pedido["vlr_frete"] or 0
                    vlr_total = pedido["vlr_total"] or 0

                    # Calculando o lucro
                    vlr_lucro = vlr_total - vlr_custo - vlr_frete

                    # Atualizando os valores no dicionário agrupado
                    if pedido["cliente_id"] != id_indicacao:
                        indicacoes_agrupadas[id_indicacao]["id_indicacao"] = id_indicacao
                        indicacoes_agrupadas[id_indicacao]["nm_indicacao"] = nm_indicacao
                        indicacoes_agrupadas[id_indicacao]["vlr_total"] += vlr_total
                        indicacoes_agrupadas[id_indicacao]["vlr_total_lucro_pedidos"] += vlr_lucro
                        indicacoes_agrupadas[id_indicacao]["qtd_indicacao"] += 1

                    if pedido["is_atleta"]:
                        indicacoes_agrupadas[id_indicacao]["vlr_custo"] += vlr_custo

                resultado_final = list(indicacoes_agrupadas.values())

                return True, "Apenas atletas agrupados com sucesso", resultado_final

        except Exception as e:
            return False, f"Erro ao buscar dados dos atletas: {str(e)}", []


