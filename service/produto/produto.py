from produto.models import Produto, Estoque, MovimentacaoEstoque
from datetime import datetime
from django.db import transaction

class ProdutoSistema():
    def listar_produtos(self, produto_id=None):
        try:
            if produto_id:
                # Busca o produto específico e a quantidade de estoque associada
                produto = Produto.objects.filter(id=produto_id).select_related('estoque').values(
                    'id', 'nome', 'codigo', 'descricao', 'preco_compra', 'preco_venda',
                    'categoria', 'estoque__quantidade', 'status'
                ).first()
                lista_produto = produto
            else:
                # Busca todos os produtos e as quantidades de estoque associadas
                lista_produto = list(
                    Produto.objects.all().select_related('estoque').values(
                        'id', 'nome', 'codigo', 'descricao', 'preco_compra', 'preco_venda',
                        'categoria', 'estoque__quantidade', 'status'
                    )
                )

            return True, 'Produtos retornados com sucesso', lista_produto
        except Exception as e:
            return False, str(e), []

    def cadastrar_produto(self, produto_id=None, nome=None, codigo=None, categoria=None, descricao=None, preco_compra=None, preco_venda=None):
        try:
            if not produto_id:
                produto_existente = Produto.objects.filter(codigo=codigo).first()
                if produto_existente:
                    return False, 'Produto com este código já cadastrado!', None

                novo_produto = Produto(
                    nome=nome,
                    codigo=codigo,
                    categoria=categoria,
                    descricao=descricao,
                    preco_compra=preco_compra,
                    preco_venda=preco_venda
                )
                novo_produto.save()

                return True, 'Produto cadastrado com sucesso!', novo_produto.id

            else:
                produto = Produto.objects.filter(id=produto_id).first()
                if not produto:
                    return False, 'Produto não encontrado!', None

                produto.nome = nome
                produto.codigo = codigo
                produto.categoria = categoria
                produto.descricao = descricao
                produto.preco_compra = preco_compra
                produto.preco_venda = preco_venda
                produto.save()

                return True, 'Produto atualizado com sucesso!', produto.id

        except Exception as e:
            return False, str(e), None

    def alterar_status_produto(self, produto_id=None):
        try:
            produto = Produto.objects.filter(id=produto_id).first()
            if produto:
                produto.status = not produto.status
                produto.save()
                return True, 'Alterado status do produto com sucesso!', produto_id
            else:
                return False, 'Produto nao encontrado', None
        except Exception as e:
            return False, str(e), None

    def alterar_estoque(self, produto_id=None, quantidade=None, movimentacao=None):
        try:
            produto = Produto.objects.filter(id=produto_id).first()
            if not produto:
                return False, 'Produto não encontrado', produto_id

            with transaction.atomic():
                estoque = Estoque.objects.filter(produto=produto).first()

                if estoque:
                    if movimentacao == 'entrada':
                        estoque.quantidade += quantidade
                    elif movimentacao == 'saida':
                        if estoque.quantidade >= quantidade:
                            estoque.quantidade -= quantidade
                        else:
                            return False, 'Quantidade insuficiente no estoque', produto_id
                else:
                    if movimentacao == 'entrada':
                        estoque = Estoque(produto=produto, quantidade=quantidade)
                    else:
                        return False, 'Estoque inexistente para saída de produto', produto_id

                estoque.data_ultima_movimentacao = datetime.now()
                estoque.save()

                movimentacao_estoque = MovimentacaoEstoque(
                    produto=produto,
                    tipo=movimentacao,
                    quantidade=quantidade,
                    data_movimentacao=datetime.now()
                )
                movimentacao_estoque.save()

            return True, 'Movimentação de estoque realizada com sucesso', produto_id
        except Exception as e:
            return False, str(e), None

    def buscar_movimentacao_estoque(self, produto_id=None):
        try:
            # Caso contrário, busca todas as movimentações
            movimentacoes = MovimentacaoEstoque.objects.all().values(
                'id', 'produto__nome', 'tipo', 'quantidade', 'data_movimentacao'
            ).order_by('-data_movimentacao')

            return True, 'Movimentações de estoque retornadas com sucesso', list(movimentacoes)
        except Exception as e:
            return False, str(e), []

