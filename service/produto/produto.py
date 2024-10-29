from produto.models import Produto, Estoque, MovimentacaoEstoque
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.db import transaction
from django.db import models

class ProdutoSistema():
    def listar_produtos(self, produto_id=None):
        try:
            ultima_movimentacao = MovimentacaoEstoque.objects.filter(
                produto_id=OuterRef('id')
            ).order_by('-data_movimentacao')

            ultima_movimentacao_tipo = Subquery(ultima_movimentacao.values('tipo')[:1])
            ultima_movimentacao_quantidade = Subquery(ultima_movimentacao.values('quantidade')[:1])
            ultima_movimentacao_data = Subquery(ultima_movimentacao.values('data_movimentacao')[:1])
            ultima_movimentacao_usuario_nome = Subquery(ultima_movimentacao.values('usuario__first_name')[:1])
            ultima_movimentacao_usuario_sobrenome = Subquery(ultima_movimentacao.values('usuario__last_name')[:1])

            if produto_id:
                produto = Produto.objects.filter(id=produto_id).select_related('estoque').annotate(
                    ultima_movimentacao_tipo=Coalesce(ultima_movimentacao_tipo, models.Value(None)),
                    ultima_movimentacao_quantidade=Coalesce(ultima_movimentacao_quantidade, models.Value(None)),
                    ultima_movimentacao_data=Coalesce(ultima_movimentacao_data, models.Value(None)),
                    ultima_movimentacao_usuario_nome=Coalesce(ultima_movimentacao_usuario_nome, models.Value(None)),
                    ultima_movimentacao_usuario_sobrenome=Coalesce(ultima_movimentacao_usuario_sobrenome,
                                                                   models.Value(None))
                ).values(
                    'id', 'nome', 'codigo', 'descricao', 'preco_compra', 'preco_venda',
                    'categoria', 'estoque__quantidade', 'status',
                    'ultima_movimentacao_tipo', 'ultima_movimentacao_quantidade', 'ultima_movimentacao_data',
                    'ultima_movimentacao_usuario_nome', 'ultima_movimentacao_usuario_sobrenome'
                ).first()
                lista_produto = produto
            else:
                lista_produto = list(
                    Produto.objects.all().select_related('estoque').annotate(
                        ultima_movimentacao_tipo=Coalesce(ultima_movimentacao_tipo, models.Value(None)),
                        ultima_movimentacao_quantidade=Coalesce(ultima_movimentacao_quantidade, models.Value(None)),
                        ultima_movimentacao_data=Coalesce(ultima_movimentacao_data, models.Value(None)),
                        ultima_movimentacao_usuario_nome=Coalesce(ultima_movimentacao_usuario_nome, models.Value(None)),
                        ultima_movimentacao_usuario_sobrenome=Coalesce(ultima_movimentacao_usuario_sobrenome,
                                                                       models.Value(None))
                    ).values(
                        'id', 'nome', 'codigo', 'descricao', 'preco_compra', 'preco_venda',
                        'categoria', 'estoque__quantidade', 'status',
                        'ultima_movimentacao_tipo', 'ultima_movimentacao_quantidade', 'ultima_movimentacao_data',
                        'ultima_movimentacao_usuario_nome', 'ultima_movimentacao_usuario_sobrenome'
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

    def alterar_estoque(self, produto_id=None, quantidade=None, movimentacao=None, usuario_id=None):
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

                estoque.data_ultima_movimentacao = timezone.now()
                estoque.usuario_id = usuario_id
                estoque.save()

                movimentacao_estoque = MovimentacaoEstoque(
                    produto=produto,
                    tipo=movimentacao,
                    quantidade=quantidade,
                    data_movimentacao=timezone.now(),
                    usuario_id=usuario_id
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

