from marca.models import Marca
from cotacao.models import Cotacao
from produto.models import Produto, Estoque, MovimentacaoEstoque
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.db import transaction
from django.db import models

class ProdutoSistema():
    def listar_produtos(self, produto_id=None):
        try:
            # Subqueries para a última movimentação
            ultima_movimentacao = MovimentacaoEstoque.objects.filter(
                produto_id=OuterRef('id')
            ).order_by('-data_movimentacao')

            ultima_movimentacao_tipo = Subquery(ultima_movimentacao.values('tipo')[:1])
            ultima_movimentacao_quantidade = Subquery(ultima_movimentacao.values('quantidade')[:1])
            ultima_movimentacao_data = Subquery(ultima_movimentacao.values('data_movimentacao')[:1])
            ultima_movimentacao_usuario_nome = Subquery(ultima_movimentacao.values('usuario__first_name')[:1])
            ultima_movimentacao_usuario_sobrenome = Subquery(ultima_movimentacao.values('usuario__last_name')[:1])

            # Filtrar por produto_id se fornecido
            if produto_id:
                produto = Produto.objects.filter(id=produto_id).select_related('estoque', 'marca').annotate(
                    ultima_movimentacao_tipo=Coalesce(ultima_movimentacao_tipo, models.Value(None)),
                    ultima_movimentacao_quantidade=Coalesce(ultima_movimentacao_quantidade, models.Value(None)),
                    ultima_movimentacao_data=Coalesce(ultima_movimentacao_data, models.Value(None)),
                    ultima_movimentacao_usuario_nome=Coalesce(ultima_movimentacao_usuario_nome, models.Value(None)),
                    ultima_movimentacao_usuario_sobrenome=Coalesce(ultima_movimentacao_usuario_sobrenome,
                                                                   models.Value(None))
                ).values(
                    'id', 'nome', 'descricao', 'preco_compra', 'preco_venda', 'marca__id',
                    'marca__nome', 'estoque__quantidade', 'status', 'preco_compra_real',
                    'ultima_movimentacao_tipo', 'ultima_movimentacao_quantidade', 'ultima_movimentacao_data',
                    'ultima_movimentacao_usuario_nome', 'ultima_movimentacao_usuario_sobrenome'
                ).first()
                lista_produto = produto
            else:
                lista_produto = list(
                    Produto.objects.all().select_related('estoque', 'marca').annotate(
                        ultima_movimentacao_tipo=Coalesce(ultima_movimentacao_tipo, models.Value(None)),
                        ultima_movimentacao_quantidade=Coalesce(ultima_movimentacao_quantidade, models.Value(None)),
                        ultima_movimentacao_data=Coalesce(ultima_movimentacao_data, models.Value(None)),
                        ultima_movimentacao_usuario_nome=Coalesce(ultima_movimentacao_usuario_nome, models.Value(None)),
                        ultima_movimentacao_usuario_sobrenome=Coalesce(ultima_movimentacao_usuario_sobrenome,
                                                                       models.Value(None))
                    ).values(
                        'id', 'nome', 'descricao', 'preco_compra', 'preco_venda',
                        'marca__nome', 'estoque__quantidade', 'status', 'preco_compra_real',
                        'ultima_movimentacao_tipo', 'ultima_movimentacao_quantidade', 'ultima_movimentacao_data',
                        'ultima_movimentacao_usuario_nome', 'ultima_movimentacao_usuario_sobrenome'
                    ).order_by("status").reverse()
                )

            return True, 'Produtos retornados com sucesso', lista_produto
        except Exception as e:
            return False, str(e), []

    def cadastrar_produto(self, produto_id=None, nome=None, marca_id=None, descricao=None, preco_compra=None,
                          preco_venda=None):
        try:
            # Verifica se está criando ou atualizando
            if not produto_id:
                # Verifica se já existe um produto com o mesmo nome e marca
                produto_existente = Produto.objects.filter(nome=nome, marca_id=marca_id).first()
                if produto_existente:
                    return False, 'Produto já cadastrado para essa marca!', None

                # Cria um novo produto
                nova_marca = Marca.objects.filter(id=marca_id).first()
                if not nova_marca:
                    return False, 'Marca não encontrada!', None

                cotacao = Cotacao.objects.all().last()

                preco_compra_real = (preco_compra * cotacao.valor) * 1.25

                novo_produto = Produto(
                    nome=nome,
                    marca=nova_marca,
                    descricao=descricao,
                    preco_compra=preco_compra,
                    preco_compra_real=preco_compra_real,
                    preco_venda=preco_venda
                )
                novo_produto.save()

                return True, 'Produto cadastrado com sucesso!', novo_produto.id

            else:
                # Atualiza o produto existente
                produto = Produto.objects.filter(id=produto_id).first()
                if not produto:
                    return False, 'Produto não encontrado!', None

                nova_marca = Marca.objects.filter(id=marca_id).first()
                if not nova_marca:
                    return False, 'Marca não encontrada!', None

                cotacao = Cotacao.objects.all().last()

                preco_compra_real = (float(preco_compra) * float(cotacao.valor)) * 1.25

                produto.nome = nome
                produto.marca = nova_marca
                produto.descricao = descricao
                produto.preco_compra = preco_compra
                produto.preco_compra_real = preco_compra_real
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
            # Filtro por produto_id, se fornecido
            movimentacoes_query = MovimentacaoEstoque.objects.all()

            if produto_id:
                movimentacoes_query = movimentacoes_query.filter(produto_id=produto_id)

            # Busca todas as movimentações com os detalhes do usuário
            movimentacoes = movimentacoes_query.values(
                'id',
                'produto__nome',
                'tipo',
                'quantidade',
                'data_movimentacao',
                'usuario__first_name',
                'usuario__last_name'
            ).order_by('-data_movimentacao')

            # Converte a queryset em uma lista de dicionários e adiciona o campo "user"
            movimentacoes_formatadas = [
                {
                    'id': mov['id'],
                    'produto__nome': mov['produto__nome'],
                    'tipo': mov['tipo'],
                    'quantidade': mov['quantidade'],
                    'data_movimentacao': mov['data_movimentacao'],
                    'user': f"{mov['usuario__first_name']} {mov['usuario__last_name']}".strip()
                }
                for mov in movimentacoes
            ]

            return True, 'Movimentações de estoque retornadas com sucesso', movimentacoes_formatadas
        except Exception as e:
            return False, str(e), []