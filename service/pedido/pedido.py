from pedido.models import Pedido, ItemPedido
from produto.models import Estoque
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db import models

class PedidoSistema():
    def listar_pedidos(self, pedido_id=None):
        try:
            if pedido_id:
                pedido_existe = Pedido.objects.filter(idPedido=pedido_id).exists()
                if not pedido_existe:
                    return False, f"Pedido com ID {pedido_id} não encontrado!", None

                # Busca o pedido com os dados gerais
                pedido = Pedido.objects.filter(idPedido=pedido_id).select_related('cliente',
                                                                                  'cliente').values(
                    'idPedido', 'dataPedido', 'vlrTotal', 'desconto',
                    'cliente__nome_completo', 'cliente__cpf_cnpj', 'cliente__email',
                    'cliente__rua', 'cliente__numero', 'cliente__complemento',
                    'cliente__bairro', 'cliente__cidade', 'cliente__estado',
                    'cliente__cep'
                ).first()

                # Organizar os dados do cliente em uma chave separada
                cliente = {
                    "nome_completo": pedido.pop('cliente__nome_completo'),
                    "cpf_cnpj": pedido.pop('cliente__cpf_cnpj'),
                    "email": pedido.pop('cliente__email'),
                    "endereco": {
                        "rua": pedido.pop('cliente__rua'),
                        "numero": pedido.pop('cliente__numero'),
                        "complemento": pedido.pop('cliente__complemento'),
                        "bairro": pedido.pop('cliente__bairro'),
                        "cidade": pedido.pop('cliente__cidade'),
                        "estado": pedido.pop('cliente__estado'),
                        "cep": pedido.pop('cliente__cep'),
                    }
                }

                pedido['cliente'] = cliente

                # Busca os produtos relacionados ao pedido
                itens = ItemPedido.objects.filter(pedido_id=pedido_id).values(
                    'produto_id', 'produto__nome', 'quantidade', 'precoUnitario', 'produto__categoria', 'produto__descricao'
                )

                # Adiciona os produtos ao resultado do pedido
                pedido['produtos'] = list(itens)
                lista_pedido = pedido
            else:
                lista_pedido = list(
                    Pedido.objects.all().select_related('cliente', 'cliente').values(
                        'idPedido', 'dataPedido', 'vlrTotal', 'desconto',
                        'cliente__nome_completo', 'cliente__cpf_cnpj', 'cliente__email',
                        'cliente__rua', 'cliente__numero', 'cliente__complemento',
                        'cliente__bairro', 'cliente__cidade', 'cliente__estado',
                        'cliente__cep'
                    )
                )

                # Organizar os dados do cliente e adicionar produtos para cada pedido
                for pedido in lista_pedido:
                    cliente = {
                        "nome_completo": pedido.pop('cliente__nome_completo'),
                        "cpf_cnpj": pedido.pop('cliente__cpf_cnpj'),
                        "email": pedido.pop('cliente__email'),
                        "endereco": {
                            "rua": pedido.pop('cliente__rua'),
                            "numero": pedido.pop('cliente__numero'),
                            "complemento": pedido.pop('cliente__complemento'),
                            "bairro": pedido.pop('cliente__bairro'),
                            "cidade": pedido.pop('cliente__cidade'),
                            "estado": pedido.pop('cliente__estado'),
                            "cep": pedido.pop('cliente__cep'),
                        }
                    }

                    pedido['cliente'] = cliente

                    itens = ItemPedido.objects.filter(pedido_id=pedido['idPedido']).values(
                        'produto_id', 'produto__nome', 'quantidade', 'precoUnitario', 'produto__categoria', 'produto__descricao'
                    )
                    pedido['produtos'] = list(itens)

            return True, 'Pedidos retornados com sucesso', lista_pedido
        except Exception as e:
            return False, str(e), []

    def cadastrar_pedido(self, pedido_id=None, data_pedido=None, cliente_id=None, itens=None, desconto=0.0):
        try:
            # Valida e ajusta o estoque para todos os itens
            for item in itens:
                produto_id = item['produto_id']
                quantidade_solicitada = item['quantidade']

                # Busca a quantidade disponível no estoque
                estoque = Estoque.objects.filter(produto_id=produto_id).first()
                if not estoque:
                    return False, f"Produto ID {produto_id} não encontrado no estoque!", None

                if estoque.quantidade < quantidade_solicitada:
                    return False, f"Estoque insuficiente para o produto ID {produto_id}! Disponível: {estoque.quantidade}, Solicitado: {quantidade_solicitada}", None

                # Se houver estoque suficiente, subtrai a quantidade solicitada
                estoque.quantidade -= quantidade_solicitada
                estoque.save()

            # Se é atualização de pedido
            if pedido_id:
                pedido = Pedido.objects.filter(idPedido=pedido_id).first()
                if not pedido:
                    return False, 'Pedido não encontrado!', None

                # Atualiza os dados do pedido
                pedido.dataPedido = data_pedido
                pedido.cliente_id = cliente_id
                pedido.desconto = desconto
                pedido.save()

                # Remove os itens antigos e ajusta o estoque
                itens_antigos = ItemPedido.objects.filter(pedido_id=pedido_id)
                for item_antigo in itens_antigos:
                    # Repor ao estoque a quantidade dos itens antigos
                    estoque = Estoque.objects.get(produto_id=item_antigo.produto_id)
                    estoque.quantidade += item_antigo.quantidade
                    estoque.save()

                itens_antigos.delete()

                # Adiciona os novos itens e mantém o ajuste no estoque já feito
                for item in itens:
                    produto_id = item['produto_id']
                    quantidade = item['quantidade']
                    preco_unitario = item['preco_unitario']

                    ItemPedido.objects.create(
                        pedido=pedido,
                        produto_id=produto_id,
                        quantidade=quantidade,
                        precoUnitario=preco_unitario
                    )

                return True, 'Pedido atualizado com sucesso!', pedido.idPedido

            # Caso seja um novo pedido
            else:
                novo_pedido = Pedido(
                    dataPedido=data_pedido,
                    cliente_id=cliente_id,
                    desconto=desconto,
                    vlrTotal=0  # O valor total será calculado abaixo
                )
                novo_pedido.save()

                vlr_total = 0
                for item in itens:
                    produto_id = item['produto_id']
                    quantidade = item['quantidade']
                    preco_unitario = item['preco_unitario']

                    vlr_total += quantidade * preco_unitario

                    ItemPedido.objects.create(
                        pedido=novo_pedido,
                        produto_id=produto_id,
                        quantidade=quantidade,
                        precoUnitario=preco_unitario
                    )

                novo_pedido.vlrTotal = vlr_total - desconto
                novo_pedido.save()

                return True, 'Pedido cadastrado com sucesso!', novo_pedido.idPedido

        except Exception as e:
            return False, str(e), None

    def deletar_pedido(self, pedido_id):
        try:
            # Busca o pedido pelo ID
            pedido = Pedido.objects.filter(idPedido=pedido_id).first()
            if not pedido:
                return False, 'Pedido não encontrado!'

            # Busca todos os itens relacionados ao pedido
            itens_pedido = ItemPedido.objects.filter(pedido_id=pedido_id)

            # Retorna os itens ao estoque
            for item in itens_pedido:
                produto_id = item.produto_id
                quantidade = item.quantidade

                # Busca o estoque do produto
                estoque = Estoque.objects.filter(produto_id=produto_id).first()
                if estoque:
                    estoque.quantidade += quantidade
                    estoque.save()

            # Remove os itens do pedido
            itens_pedido.delete()

            # Remove o pedido
            pedido.delete()

            return True, 'Pedido deletado com sucesso!'

        except Exception as e:
            return False, str(e)