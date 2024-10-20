from produto.models import Produto

class ProdutoSistema():
    def listar_produtos(self, produto_id=None):
        try:
            if produto_id:
                lista_produto = Produto.objects.filter(id=produto_id).values().first()
            else:
                lista_produto = list(Produto.objects.all().values())
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