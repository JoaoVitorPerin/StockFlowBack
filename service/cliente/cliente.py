from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from cliente.models import Cliente

class ClienteSistema():
    def listar_clientes(self, cliente_id=None):
        try:
            # Subquery para buscar a última indicação
            ultima_indicacao = Cliente.objects.filter(
                indicados=OuterRef('id')  # Supondo que 'indicados' é o campo de referência
            ).order_by('-id')

            ultima_indicacao_nome = Subquery(ultima_indicacao.values('nome_completo')[:1])
            ultima_indicacao_cpf_cnpj = Subquery(ultima_indicacao.values('cpf_cnpj')[:1])
            cliente_indicador_id = Subquery(ultima_indicacao.values('id')[:1])  # Novo nome para evitar conflitos

            if cliente_id:
                cliente = Cliente.objects.filter(id=cliente_id).annotate(
                    ultima_indicacao_nome=Coalesce(ultima_indicacao_nome, Value(None)),
                    ultima_indicacao_cpf_cnpj=Coalesce(ultima_indicacao_cpf_cnpj, Value(None)),
                    cliente_indicador=Coalesce(cliente_indicador_id, Value(None))  # Usa um nome diferente
                ).values(
                    'id', 'nome_completo', 'cpf_cnpj', 'telefone', 'email',
                    'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep',
                    'is_atleta', 'ultima_indicacao_nome', 'ultima_indicacao_cpf_cnpj', 'status', 'cliente_indicador'
                ).first()
                lista_clientes = cliente
            else:
                lista_clientes = list(
                    Cliente.objects.all().annotate(
                        ultima_indicacao_nome=Coalesce(ultima_indicacao_nome, Value(None)),
                        ultima_indicacao_cpf_cnpj=Coalesce(ultima_indicacao_cpf_cnpj, Value(None)),
                        cliente_indicador=Coalesce(cliente_indicador_id, Value(None))  # Usa um nome diferente
                    ).values(
                        'id', 'nome_completo', 'cpf_cnpj', 'telefone', 'email',
                        'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep',
                        'is_atleta', 'ultima_indicacao_nome', 'ultima_indicacao_cpf_cnpj', 'status', 'cliente_indicador'
                    ).order_by('id')
                )

            return True, 'Clientes retornados com sucesso', lista_clientes
        except Exception as e:
            return False, str(e), []

    def cadastrar_cliente(
            self, cliente_id=None, nome_completo=None, cpf_cnpj=None, telefone=None, email=None,
            rua=None, numero=None, complemento=None, bairro=None, cidade=None, estado=None, cep=None,
            indicacao=None, is_atleta=False
    ):
        try:
            indicacaoInstance = Cliente.objects.filter(id=indicacao).first() if indicacao else None

            if not cliente_id :
                cliente_existente = Cliente.objects.filter(cpf_cnpj=cpf_cnpj).first()
                if cliente_existente and cpf_cnpj:
                    return False, 'Cliente com este CPF/CNPJ já cadastrado!', None

                cliente_existente_email = Cliente.objects.filter(email=email).first()
                if cliente_existente_email and email:
                    return False, 'Cliente com este email já cadastrado!', None

                novo_cliente = Cliente(
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
                    indicacao=indicacaoInstance,
                    is_atleta=is_atleta
                )
                novo_cliente.save()

                return True, 'Cliente cadastrado com sucesso!', novo_cliente.id

            else:
                cliente = Cliente.objects.filter(id=cliente_id).first()
                if not cliente:
                    return False, 'Cliente não encontrado!', None

                cliente_existente = Cliente.objects.filter(cpf_cnpj=cpf_cnpj).first()
                if cliente_existente and cpf_cnpj:
                    return False, 'Cliente com este CPF/CNPJ já cadastrado!', None

                cliente_existente_email = Cliente.objects.filter(email=email).first()
                if cliente_existente_email and email:
                    return False, 'Cliente com este email já cadastrado!', None

                cliente.nome_completo = nome_completo
                cliente.cpf_cnpj = cpf_cnpj
                cliente.telefone = telefone
                cliente.email = email
                cliente.rua = rua
                cliente.numero = numero
                cliente.complemento = complemento
                cliente.bairro = bairro
                cliente.cidade = cidade
                cliente.estado = estado
                cliente.cep = cep
                cliente.indicacao = indicacaoInstance
                cliente.is_atleta = is_atleta
                cliente.save()

                return True, 'Cliente atualizado com sucesso!', cliente.id

        except Exception as e:
            return False, str(e), None

    def alterar_status_cliente(self, cliente_id=None):
        try:
            cliente = Cliente.objects.filter(id=cliente_id).first()

            if cliente:
                cliente.status = not cliente.status
                cliente.save()
                return True, 'Status do cliente alterado com sucesso!', cliente_id
            else:
                return False, 'Cliente não encontrado', None
        except Exception as e:
            return False, str(e), None