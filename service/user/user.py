from django.contrib.auth.models import User

class Usuario():
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def cadastrar_usuario(self, nome=None, sobrenome=None, email=None):
        try:
            usuario = User(username=self.username)

            if self.password:
                usuario.set_password(raw_password=self.password)

            usuario.first_name = nome
            usuario.last_name = sobrenome
            usuario.email = email
            usuario.save()

            return True, 'Usuário cadastrado com sucesso', usuario.id
        except Exception as e:
            return False, str(e), None


    def listar_usuarios(self, user_id=None):
        try:
            if(user_id):
                lista_usuario = User.objects.values().filter(id=user_id).values('username', 'email','id','first_name','last_name').first()
            else:
                lista_usuario = list(User.objects.all().values('username', 'email','id','first_name','last_name'))
            return True, 'Usuários retornados com sucesso', lista_usuario
        except Exception as e:
            return False, str(e), []