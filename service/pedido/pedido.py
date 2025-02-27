from django.utils import timezone

from pedido.models import Pedido, ItemPedido
from produto.models import Estoque, MovimentacaoEstoque, Produto
from django.db.models import Prefetch
from django.forms.models import model_to_dict

class PedidoSistema():
    def listar_pedidos(self, pedido_id=None):
        try:
            if pedido_id:
                pedido_existe = Pedido.objects.filter(idPedido=pedido_id).exists()
                if not pedido_existe:
                    return False, f"Pedido com ID {pedido_id} não encontrado!", None

                # Busca o pedido com todos os campos
                pedido_obj = Pedido.objects.select_related('cliente').get(idPedido=pedido_id)
                pedido = model_to_dict(pedido_obj)

                # Organizar os dados do cliente em uma chave separada
                cliente = model_to_dict(pedido_obj.cliente)
                cliente['endereco'] = {
                    "logradouro": pedido_obj.logradouro,  # Dados diretamente do modelo Pedido
                    "numero": pedido_obj.numero,
                    "complemento": pedido_obj.complemento,
                    "bairro": pedido_obj.bairro,
                    "cidade": pedido_obj.localidade,
                    "estado": pedido_obj.uf,
                    "cep": pedido_obj.cep,
                }

                pedido['cliente'] = cliente

                # Busca os produtos relacionados ao pedido
                itens = ItemPedido.objects.filter(pedido_id=pedido_id).select_related('produto').values(
                    'produto_id', 'produto__nome', 'quantidade', 'precoUnitario', 'precoCusto',
                    'produto__marca_id', 'produto__descricao', 'is_estoque_externo'
                )

                # Adiciona os produtos ao resultado do pedido
                pedido['produtos'] = list(itens)
                lista_pedido = pedido
            else:
                pedidos = Pedido.objects.select_related('cliente').prefetch_related(
                    Prefetch('itens', queryset=ItemPedido.objects.select_related('produto', 'produto__marca'), to_attr='itens_prefetch')
                ).order_by('-idPedido')

                lista_pedido = []

                for pedido_obj in pedidos:
                    pedido = {
                        "idPedido": pedido_obj.idPedido,
                        "dataPedido": pedido_obj.dataPedido,
                        "frete": pedido_obj.frete,
                        "desconto": pedido_obj.desconto,
                        "status": pedido_obj.status,
                        "vlr_total": pedido_obj.vlrTotal
                    }

                    cliente = {
                        "id": pedido_obj.cliente.id,
                        "nome_completo": pedido_obj.cliente.nome_completo,
                        "email": pedido_obj.cliente.email,
                        "endereco": {
                            "logradouro": pedido_obj.logradouro,
                            "numero": pedido_obj.numero,
                            "complemento": pedido_obj.complemento,
                            "bairro": pedido_obj.bairro,
                            "cidade": pedido_obj.localidade,
                            "estado": pedido_obj.uf,
                            "cep": pedido_obj.cep,
                        }
                    }

                    pedido["cliente"] = cliente

                    pedido["produtos"] = [
                        {
                            "produto_id": item.produto.id,
                            "nome": item.produto.nome,
                            "quantidade": item.quantidade,
                            "precoUnitario": item.precoUnitario,
                            "precoCusto": item.precoCusto,
                            "marca_id": item.produto.marca.id,
                            "marca_nome": item.produto.marca.nome,
                            "descricao": item.produto.descricao,
                            "is_estoque_externo": item.is_estoque_externo,
                        }
                        for item in pedido_obj.itens_prefetch
                    ]

                    lista_pedido.append(pedido)

            return True, 'Pedidos retornados com sucesso', lista_pedido
        except Exception as e:
            return False, str(e), []

    def cadastrar_pedido(self, pedido_id=None, data_pedido=None, cliente_id=None, itens=None, desconto=0.0, frete=0.0, usuario_id=None,
                         logradouro=None, numero=None, complemento=None, bairro=None, localidade=None, uf=None, vlr_total=None,
                         cep=None):
        try:
            # Valida e ajusta o estoque para todos os itens
            for item in itens:
                produto_id = item['produto_id']
                quantidade_solicitada = item['quantidade']
                is_estoque_externo = item['is_estoque_externo']

                if is_estoque_externo:
                    continue

                # Busca a quantidade disponível no estoque
                estoque = Estoque.objects.filter(produto_id=produto_id).first()
                if not estoque:
                    return False, f"Produto ID {produto_id} não encontrado no estoque!", None

                if estoque.quantidade < quantidade_solicitada:
                    return False, f"Estoque insuficiente para o produto ID {produto_id}! Disponível: {estoque.quantidade}, Solicitado: {quantidade_solicitada}", None

                # Se houver estoque suficiente, subtrai a quantidade solicitada
                estoque.quantidade -= quantidade_solicitada
                estoque.save()

                produto = Produto.objects.filter(id=produto_id).first()
                movimentacao_estoque = MovimentacaoEstoque(
                    produto=produto,
                    tipo='saida',
                    quantidade=quantidade_solicitada,
                    data_movimentacao=timezone.now(),
                    usuario_id=usuario_id
                )
                movimentacao_estoque.save()

            # Dentro do bloco "Se é atualização de pedido"
            if pedido_id:
                pedido = Pedido.objects.filter(idPedido=pedido_id).first()
                if not pedido:
                    return False, 'Pedido não encontrado!', None

                # Atualiza os dados do pedido
                pedido.dataPedido = data_pedido
                pedido.cliente_id = cliente_id
                pedido.desconto = desconto
                pedido.frete = frete
                pedido.vlrTotal = vlr_total

                # Atualiza os campos de endereço
                pedido.logradouro = logradouro
                pedido.numero = numero
                pedido.complemento = complemento
                pedido.bairro = bairro
                pedido.localidade = localidade
                pedido.uf = uf
                pedido.cep = cep
                pedido.status = 'separacao'

                pedido.save()

                # Ajusta o estoque para os itens antigos antes de apagar
                itens_antigos = ItemPedido.objects.filter(pedido_id=pedido_id)
                for item_antigo in itens_antigos:
                    # Repor ao estoque a quantidade dos itens antigos, caso não fossem de estoque externo
                    if not item_antigo.is_estoque_externo:
                        estoque = Estoque.objects.filter(produto_id=item_antigo.produto_id).first()
                        if estoque:
                            estoque.quantidade += item_antigo.quantidade
                            estoque.save()

                            produto = Produto.objects.filter(id=produto_id).first()
                            movimentacao_estoque = MovimentacaoEstoque(
                                produto=produto,
                                tipo='entrada',
                                quantidade=item_antigo.quantidade,
                                data_movimentacao=timezone.now(),
                                usuario_id=usuario_id
                            )
                            movimentacao_estoque.save()

                # Remove os itens antigos do pedido
                itens_antigos.delete()

                # Processa os novos itens do pedido
                for item in itens:
                    produto_id = item['produto_id']
                    quantidade = item['quantidade']
                    preco_unitario = item['preco_unitario']
                    is_estoque_externo = item['is_estoque_externo']
                    preco_custo = item['preco_custo']

                    # Cria o novo item no pedido
                    ItemPedido.objects.create(
                        pedido=pedido,
                        produto_id=produto_id,
                        quantidade=quantidade,
                        precoUnitario=preco_unitario,
                        precoCusto=preco_custo,
                        is_estoque_externo=is_estoque_externo
                    )

                return True, 'Pedido atualizado com sucesso!', pedido.idPedido

            # Caso seja um novo pedido
            else:
                novo_pedido = Pedido(
                    dataPedido=data_pedido,
                    cliente_id=cliente_id,
                    desconto=desconto,
                    frete=frete,
                    vlrTotal=vlr_total,
                    logradouro=logradouro,
                    numero=numero,
                    complemento=complemento,
                    bairro=bairro,
                    localidade=localidade,
                    uf=uf,
                    cep=cep,
                    status='separacao'
                )
                novo_pedido.save()

                vlr_total = 0
                for item in itens:
                    produto_id = item['produto_id']
                    quantidade = item['quantidade']
                    preco_unitario = item['preco_unitario']
                    is_estoque_externo = item['is_estoque_externo']
                    preco_custo = item['preco_custo']

                    ItemPedido.objects.create(
                        pedido=novo_pedido,
                        produto_id=produto_id,
                        quantidade=quantidade,
                        precoUnitario=preco_unitario,
                        precoCusto=preco_custo,
                        is_estoque_externo=is_estoque_externo
                    )

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

    def alterar_status_pedido(self, pedidos=None):
        #status 1 = separacao
        #status 2 = embalado
        #status 3 = saiu_estoque
        try:
            for pedido in pedidos:
                pedido = Pedido.objects.filter(idPedido=pedido).first()
                if not pedido:
                    continue

                if(pedido.status == 'separacao'):
                    pedido.status = 'embalado'
                elif(pedido.status == 'embalado'):
                    pedido.status = 'saiu_estoque'
                pedido.save()
            return True, 'Status do pedido atualizado com sucesso!'
        except Exception as e:
            return False, str(e)