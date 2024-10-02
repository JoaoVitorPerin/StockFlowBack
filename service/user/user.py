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

            return True, ''
        except Exception as e:
            return False, str(e)
