from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from StockFlowBack.decorators import group_required
from django.utils.decorators import method_decorator
import service.cliente.cliente
from django.http import JsonResponse

class ClienteCadastoView(APIView):
    @method_decorator(group_required('Administrador', 'Operador de Estoque', 'Operador de Pedidos'))
    def get(self, *args, **kwargs):
        cliente_id = self.request.GET.get('cliente_id')
        status, mensagem, clientes = service.cliente.cliente.ClienteSistema().listar_clientes(cliente_id=cliente_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'clientes': clientes})

    @method_decorator(group_required('Administrador', 'Operador de Estoque', 'Operador de Pedidos'))
    def post(self, *args, **kwargs):
        cliente_id = self.request.data.get('cliente_id')
        nome_completo = self.request.data.get('nome_completo')
        cpf_cnpj = self.request.data.get('cpf_cnpj')
        telefone = self.request.data.get('telefone')
        email = self.request.data.get('email')
        rua = self.request.data.get('logradouro')
        numero = self.request.data.get('numero')
        complemento = self.request.data.get('complemento')
        bairro = self.request.data.get('bairro')
        cidade = self.request.data.get('localidade')
        estado = self.request.data.get('uf')
        cep = self.request.data.get('cep')
        indicacao = self.request.data.get('cliente_indicador')
        is_atleta = self.request.data.get('is_atleta')

        status, mensagem, cliente_id = service.cliente.cliente.ClienteSistema().cadastrar_cliente(cliente_id=cliente_id,
                                                                                                  nome_completo=nome_completo,
                                                                                                  cpf_cnpj=cpf_cnpj,
                                                                                                  telefone=telefone,
                                                                                                  email=email,
                                                                                                  rua=rua,
                                                                                                  numero=numero,
                                                                                                  complemento=complemento,
                                                                                                  bairro=bairro,
                                                                                                  cidade=cidade,
                                                                                                  estado=estado,
                                                                                                  cep=cep,
                                                                                                  indicacao=indicacao,
                                                                                                  is_atleta=is_atleta)

        return JsonResponse({'status': status, 'descricao': mensagem, 'cliente_id': cliente_id})

    @method_decorator(group_required('Administrador', 'Operador de Estoque', 'Operador de Pedidos'))
    def delete(self, *args, **kwargs):
        cliente_id = self.request.GET.get('cliente_id')

        status, mensagem, cliente_id = service.cliente.cliente.ClienteSistema().alterar_status_cliente(cliente_id=cliente_id)

        return JsonResponse({'status': status, 'descricao': mensagem, 'cliente_id': cliente_id})