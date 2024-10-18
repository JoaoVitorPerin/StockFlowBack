from user.models import Usuario
from django.utils import timezone
from django.contrib.auth.models import Group
from django.db import models

class UsuarioSistema():
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def cadastrar_usuario(self, username=None, user_id=None, nome=None, sobrenome=None, email=None, grupo_id=None):
        try:
            if not user_id:
                # Verificar se o nome de usuário já existe
                isUsernameExistente = Usuario.objects.filter(username=username).first()
                if isUsernameExistente:
                    return False, 'Usuário já cadastrado!', None

                # Criar um novo usuário
                usuario = Usuario(username=username)

                if self.password:
                    usuario.set_password(raw_password=self.password)

                usuario.first_name = nome
                usuario.last_name = sobrenome
                usuario.email = email
                usuario.save()

                # Associar o usuário ao grupo (se o grupo_id for fornecido)
                if grupo_id:
                    try:
                        grupo = Group.objects.get(id=grupo_id)
                        usuario.groups.add(grupo)
                    except Group.DoesNotExist:
                        return False, 'Grupo não encontrado!', None

                return True, 'Usuário cadastrado com sucesso!', usuario.id

            else:
                # Atualizar um usuário existente
                usuario = Usuario.objects.filter(id=user_id).first()

                if not usuario:
                    return False, 'Usuário não encontrado!', None

                usuario.first_name = nome
                usuario.last_name = sobrenome
                usuario.email = email
                usuario.save()

                # Atualizar o grupo do usuário (se o grupo_id for fornecido)
                if grupo_id:
                    try:
                        grupo = Group.objects.get(id=grupo_id)
                        usuario.groups.clear()  # Remover todos os grupos atuais
                        usuario.groups.add(grupo)
                    except Group.DoesNotExist:
                        return False, 'Grupo não encontrado!', None

                return True, 'Usuário atualizado com sucesso!', usuario.id
        except Exception as e:
            return False, str(e), None

    def deletar_usuario(self, user_id=None):
        try:
            if not user_id:
                return False, 'Informe o user id!', None

            usuario = Usuario.objects.filter(id=user_id).first()

            if not usuario:
                return False, 'Usuário não encontrado!', None

            usuario.delete()

            return True, 'Usuário excluído com sucesso!', None
        except Exception as e:
            return False, str(e), None


        except Exception as e:
            return False, str(e), None

    def listar_usuarios(self, user_id=None):
        try:
            if user_id:
                # Buscar um único usuário e renomear 'groups__id' para 'group_id'
                lista_usuario = Usuario.objects.filter(id=user_id, is_active=True).values(
                    'username', 'email', 'id', 'first_name', 'last_name', 'groups__id'
                ).annotate(grupo_id=models.F('groups__id')).first()
            else:
                # Buscar todos os usuários e renomear 'groups__id' para 'group_id'
                lista_usuario = list(Usuario.objects.all().values(
                    'username', 'email', 'id', 'first_name', 'last_name', 'groups__id'
                ).annotate(grupo_id=models.F('groups__id')))
            return True, 'Usuários retornados com sucesso', lista_usuario
        except Exception as e:
            return False, str(e), []

    def resetar_senha(self, email=None, codigo=None, senha=None):
        try:
            if email:
                # Buscar o usuário pelo email
                usuario = Usuario.objects.filter(email=email).first()
                if usuario:
                    # Verificar se o código está correto e se o token ainda é válido
                    if usuario.codigo_reset == codigo:
                        if timezone.now() < usuario.validade_codigo:
                            # Definir a nova senha
                            usuario.set_password(raw_password=senha)
                            usuario.codigo_reset = None
                            usuario.validade_codigo = None
                            usuario.save()  # Salvar as mudanças no banco de dados
                            return True, 'Senha redefinida com sucesso!'
                        else:
                            return False, 'O código de recuperação expirou'
                    else:
                        return False, 'Código de recuperação inválido'
                else:
                    return False, 'Nenhum usuário encontrado com esse email'
            else:
                return False, 'Informe um email'
        except Exception as e:
            return False, str(e), []

    def buscar_todos_os_grupos(self):
        try:
            grupos = Group.objects.all()
            lista_grupos = [{'id': grupo.id, 'name': grupo.name} for grupo in grupos]

            return True, 'Grupos retornados com sucesso!', lista_grupos
        except Exception as e:
            return False, str(e), []