from django.contrib.auth.models import User

class Usuario():
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def cadastrar_usuario(self,username=None, user_id=None, nome=None, sobrenome=None, email=None):
        try:
            if not user_id:
                isUsernameExistente = User.objects.filter(username=username).first()
                if(isUsernameExistente):
                    return False, 'Usuário já cadastrado!', None

                usuario = User(username=self.username)

                if self.password:
                    usuario.set_password(raw_password=self.password)

                usuario.username = username
                usuario.first_name = nome
                usuario.last_name = sobrenome
                usuario.email = email
                usuario.save()
                return True, 'Usuário cadastrado com sucesso!', usuario.id
            else:
                usuario = User.objects.filter(id=user_id).first()

                if not usuario:
                    return False, 'Usuário não encontrado!', None

                usuario.first_name = nome
                usuario.last_name = sobrenome
                usuario.email = email
                usuario.save()

                return True, 'Usuário atualizado com sucesso!', usuario.id
        except Exception as e:
            return False, str(e), None

    def deletar_usuario(self, user_id=None):
        try:
            if not user_id:
                return False, 'Informe o user id!', None

            usuario = User.objects.filter(id=user_id).first()

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
            if(user_id):
                lista_usuario = User.objects.values().filter(id=user_id, is_active=True).values('username', 'email','id','first_name','last_name').first()
            else:
                lista_usuario = list(User.objects.all().values('username', 'email','id','first_name','last_name'))
            return True, 'Usuários retornados com sucesso', lista_usuario
        except Exception as e:
            return False, str(e), []