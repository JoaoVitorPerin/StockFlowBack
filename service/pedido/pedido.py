from pedido.models import Pedido, ItemPedido
from produto.models import Estoque
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db import models
from django.forms.models import model_to_dict

class PedidoSistema():
    from django.forms.models import model_to_dict

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
                    'produto_id', 'produto__nome', 'quantidade', 'precoUnitario',
                    'produto__marca_id', 'produto__descricao', 'is_estoque_externo'
                )

                # Adiciona os produtos ao resultado do pedido
                pedido['produtos'] = list(itens)
                lista_pedido = pedido
            else:
                pedidos = Pedido.objects.select_related('cliente').all()
                lista_pedido = []

                for pedido_obj in pedidos:
                    pedido = model_to_dict(pedido_obj)

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

                    itens = ItemPedido.objects.filter(pedido_id=pedido['idPedido']).select_related('produto').values(
                        'produto_id', 'produto__nome', 'quantidade', 'precoUnitario',
                        'produto__marca_id', 'produto__marca__nome', 'produto__descricao', 'is_estoque_externo'
                    )

                    pedido['produtos'] = list(itens)
                    lista_pedido.append(pedido)

            return True, 'Pedidos retornados com sucesso', lista_pedido
        except Exception as e:
            return False, str(e), []

    def cadastrar_pedido(self, pedido_id=None, data_pedido=None, cliente_id=None, itens=None, desconto=0.0, frete=0.0,
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

                # Remove os itens antigos do pedido
                itens_antigos.delete()

                # Processa os novos itens do pedido
                for item in itens:
                    produto_id = item['produto_id']
                    quantidade = item['quantidade']
                    preco_unitario = item['preco_unitario']
                    is_estoque_externo = item['is_estoque_externo']

                    # Cria o novo item no pedido
                    ItemPedido.objects.create(
                        pedido=pedido,
                        produto_id=produto_id,
                        quantidade=quantidade,
                        precoUnitario=preco_unitario,
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

                    ItemPedido.objects.create(
                        pedido=novo_pedido,
                        produto_id=produto_id,
                        quantidade=quantidade,
                        precoUnitario=preco_unitario,
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

    def alterar_status_pedido(self, pedido_id):
        #status 1 = separacao
        #status 2 = embalado
        #status 3 = saiu_estoque
        try:
            pedido = Pedido.objects.filter(idPedido=pedido_id).first()
            if not pedido:
                return False, 'Pedido não encontrado!'

            if(pedido.status == 'separacao'):
                pedido.status = 'embalado'
            elif(pedido.status == 'embalado'):
                pedido.status = 'saiu_estoque'
            else:
                return False, 'Pedido já se encontra no status de saida de estoque!'
            pedido.save()
            return True, 'Status do pedido atualizado com sucesso!'
        except Exception as e:
            return False, str(e)