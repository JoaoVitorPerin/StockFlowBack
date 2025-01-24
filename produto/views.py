from rest_framework.views import APIView
from django.http import JsonResponse
import service.produto.produto
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny, IsAuthenticated

class ProdutoCadastoView(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def get(self, *args, **kwargs):
        produto_id = self.request.GET.get('produto_id')
        status, mensagem, produtos = service.produto.produto.ProdutoSistema().listar_produtos(produto_id=produto_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'produtos': produtos})

    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def post(self, *args, **kwargs):
        produto_id = self.request.data.get('produto_id')
        nome = self.request.data.get('nome')
        marca_id = self.request.data.get('marca__id')
        descricao = self.request.data.get('descricao')
        preco_compra = self.request.data.get('preco_compra')
        preco_venda = self.request.data.get('preco_venda')

        status, mensagem, produto_id = service.produto.produto.ProdutoSistema().cadastrar_produto(produto_id=produto_id,
                                                                                        nome=nome,
                                                                                        marca_id=marca_id,
                                                                                        descricao=descricao,
                                                                                        preco_compra=preco_compra,
                                                                                        preco_venda=preco_venda)

        return JsonResponse({'status': status, 'descricao':mensagem, 'produto_id': produto_id})

    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def delete(self, *args, **kwargs):
        produto_id = self.request.GET.get('produto_id')

        status, mensagem, produto_id = service.produto.produto.ProdutoSistema().alterar_status_produto(produto_id=produto_id)

        return JsonResponse({'status': status, 'descricao': mensagem, 'produto_id': produto_id})

class ProdutoEstoqueView(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def get(self, *args, **kwargs):
        status, mensagem, lista = service.produto.produto.ProdutoSistema().buscar_movimentacao_estoque()
        return JsonResponse({'status': status, 'descricao': mensagem, 'movimentacao': lista})


    @method_decorator(group_required('Administrador', 'Operador de Estoque'))
    def post(self, *args, **kwargs):
        produto_id = self.request.data.get('produto_id')
        quantidade = self.request.data.get('quantidade')
        movimentacao = self.request.data.get('movimentacao')
        usuario_id = self.request.data.get('usuario_id')

        status, mensagem, produto_id = service.produto.produto.ProdutoSistema().alterar_estoque(produto_id=produto_id,
                                                                                                quantidade=quantidade,
                                                                                                movimentacao=movimentacao,
                                                                                                usuario_id=usuario_id)
        return JsonResponse({'status': status, 'descricao': mensagem, 'produto_id': produto_id})