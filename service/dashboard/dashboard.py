from produto.models import Estoque
from django.db.models import Sum
from collections import defaultdict
from django.db.models import F, Prefetch, Q
from django.utils.timezone import make_aware
from datetime import datetime
from pedido.models import Pedido, ItemPedido
from cliente.models import Cliente
from custo_mensal.models import CustoMensal
from django.db.models.functions import Coalesce
from dateutil.relativedelta import relativedelta
import math

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

    def buscar_dados_estoque_coeficiente_compra_produto(self):
        try:
            hoje = datetime.today()

            inicio_mes_atual = datetime(hoje.year, hoje.month, 1)
            data_inicio_3_meses = make_aware(inicio_mes_atual - relativedelta(months=3))
            data_fim_3_meses = make_aware(inicio_mes_atual)

            # ------------------------------
            # 1. Consulta de vendas dos últimos 3 meses por produto
            # ------------------------------
            media_vendas_produtos = list(ItemPedido.objects.filter(
                pedido__dataPedido__gte=data_inicio_3_meses,
                pedido__dataPedido__lt=data_fim_3_meses
            ).values(
                id=F("produto_id"),
                nome_produto=F("produto_id__nome"),
                marca=F("produto_id__marca__nome")
            ).annotate(
                total_vendido_ultimos_3_meses=Coalesce(Sum("quantidade"), 0),
            ).annotate(
                media_mensal=F("total_vendido_ultimos_3_meses") / 3.0
            ).order_by("-media_mensal"))

            # ------------------------------
            # 2. Consulta de estoque atual por produto
            # ------------------------------
            estoque_por_produto = {
                item["produto_id"]: item
                for item in Estoque.objects.values(
                    "produto_id",
                    "quantidade",
                )
            }

            # ------------------------------
            # 3. Mesclar as duas listas com base no produto_id
            # ------------------------------
            produtos_com_estoque = []

            for produto in media_vendas_produtos:
                produto_id = produto["id"]
                estoque = estoque_por_produto.get(produto_id, {})

                produto["quantidade_estoque"] = estoque.get("quantidade", 0)

                # 💡 Cálculo do coeficiente de estoque
                if produto["media_mensal"] > 0 and produto["quantidade_estoque"] > 0:
                    produto["coef_estoque"] = round(produto["quantidade_estoque"] / produto["media_mensal"], 2)
                else:
                    produto["coef_estoque"] = 0

                media = float(produto.get("media_mensal") or 0)
                estoque = float(produto.get("quantidade_estoque") or 0)

                # Previsão base
                if estoque >= 0:
                    previsao = (media * 1.75) - estoque
                else:
                    previsao = (media * 1.75) + abs(estoque)

                # Arredondar para cima se for maior que 0
                produto["previsao_compra"] = math.ceil(previsao) if previsao > 0 else 0

                produtos_com_estoque.append(produto)

            produtos_com_estoque.sort(key=lambda item: item["coef_estoque"])
            return True, 'Produtos com média de venda e estoque retornados com sucesso!', produtos_com_estoque

        except Exception as e:
            return False, f"Erro ao buscar dados: {str(e)}", []

class DashboardVendas:
    @staticmethod
    def buscar_dados_vendas(anomes=None):
        try:
            mes = anomes[4:]
            ano = anomes[:4]

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

            atletas_com_pedido = set()

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
                    atletas_com_pedido.add(pedido["nm_cliente"])  # salvar nome do atleta com pedido
                else:
                    qtd_pedidos_nao_atleta += 1

            # Agora buscar todos os atletas
            todos_atletas = Cliente.objects.filter(is_atleta=True).values_list('nome_completo', flat=True)

            atletas_sem_pedido = set(todos_atletas) - atletas_com_pedido

            for nome_atleta in atletas_sem_pedido:
                pedidos_com_itens.append({
                    "dataPedido": None,
                    "idPedido": None,
                    "nm_cliente": nome_atleta,
                    "is_atleta": True,
                    "vlr_frete": 0,
                    "vlr_custo": 0,
                    "vlr_total": 0,
                    "vlr_lucro": 0,
                    "vlr_margem": 0,
                })

            anomes_date = datetime.strptime(str(anomes), "%Y%m")

            total_custo_fixo = (
                CustoMensal.objects.filter(
                    Q(recorrente=True) |
                    Q(dat_ini__year__lte=anomes_date.year, dat_ini__month__lte=anomes_date.month) &
                    (Q(dat_fim__year__gte=anomes_date.year, dat_fim__month__gte=anomes_date.month) | Q(dat_fim__isnull=True))
                ).aggregate(total=Sum("valor"))["total"] or 0
            )
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

            custos = list(
                CustoMensal.objects.filter(
                    Q(recorrente=True) |
                    Q(dat_ini__year__lte=anomes_date.year, dat_ini__month__lte=anomes_date.month) &
                    (Q(dat_fim__year__gte=anomes_date.year, dat_fim__month__gte=anomes_date.month) | Q(dat_fim__isnull=True))
                ).values().order_by('id')
            )

            retorno = {
                "pedidos": pedidos_com_itens,
                "custos_mensais": custos,
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

class DashboardVendasMarca():
    def buscar_dados_vendas_marcas(self, marca_id=None, anomes=None):
        try:
            mes = anomes[4:]
            ano = anomes[:4]

            data_inicio = make_aware(datetime(int(ano), int(mes), 1, 0, 0, 0))
            if int(mes) == 12:
                data_fim = make_aware(datetime(int(ano) + 1, 1, 1, 0, 0, 0))
            else:
                data_fim = make_aware(datetime(int(ano), int(mes) + 1, 1, 0, 0, 0))

            # Buscar itens dos pedidos no período com marca do produto filtrada
            itens = ItemPedido.objects.filter(
                pedido__dataPedido__gte=data_inicio,
                pedido__dataPedido__lt=data_fim,
                produto__marca_id=marca_id
            ).select_related('produto').annotate(
                nome_produto=F("produto__nome"),
            ).values(
                "produto_id",
                "nome_produto"
            ).annotate(
                qtd_produto=Sum("quantidade"),
                vlr_venda_total=Sum(F("precoUnitario") * F("quantidade")),
                vlr_custo_total=Sum(F("precoCusto") * F("quantidade")),
            ).order_by("nome_produto")

            lista_produtos = list(itens)

            # Calcular totais agregados
            total_venda = sum(p["vlr_venda_total"] for p in lista_produtos)
            total_custo = sum(p["vlr_custo_total"] for p in lista_produtos)
            total_qtd = sum(p["qtd_produto"] for p in lista_produtos)

            margem_percentual = round(((total_venda - total_custo) / total_venda) * 100, 2) if total_venda > 0 else 0

            resumo_valores = {
                "vlr_venda_somado": total_venda,
                "vlr_custo_somado": total_custo,
                "qtd_somada": total_qtd,
                "margem_percentual": margem_percentual
            }

            retorno = {
                "resumo_valores": resumo_valores,
                "lista_produtos": lista_produtos
            }

            mensagem = f"Resumo e lista de produtos vendidos da marca {marca_id} para {mes}/{ano} retornados com sucesso!"
            return True, mensagem, retorno

        except Exception as e:
            return False, f"Erro ao buscar dados de vendas por marca: {str(e)}", []