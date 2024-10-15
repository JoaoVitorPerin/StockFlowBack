from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from StockFlowBack.serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import service.user.user
import service.email.email
from dotenv import load_dotenv
import os
import random

load_dotenv()

class UserCadastoView(APIView):
    def get(self, *args, **kwargs):
        user_id = self.request.GET.get('user_id')
        status, mensagem, usuarios = service.user.user.Usuario().listar_usuarios(user_id=user_id)

        return JsonResponse({'status': status, 'mensagem': mensagem, 'usuario': usuarios})

    def post(self, *args, **kwargs):
        user_id = self.request.data.get('user_id')
        username = self.request.data.get('username')
        password = os.getenv('STOCKFLOW_DEFAULT_PASSWORD')
        nome = self.request.data.get('first_name')
        sobrenome = self.request.data.get('last_name')
        email = self.request.data.get('email')

        status, mensagem, user_id = service.user.user.Usuario(username=username, password=password).cadastrar_usuario(user_id=user_id,
                                                                                                                      username=username,
                                                                                                                      nome=nome,
                                                                                                                      sobrenome=sobrenome,
                                                                                                                      email=email)

        return JsonResponse({'status': status, 'descricao':mensagem, 'user_id': user_id})

    def delete(self, *args, **kwargs):
        user_id = self.request.GET.get('user_id')

        status, mensagem, user_id = service.user.user.Usuario().deletar_usuario(user_id=user_id)

        return JsonResponse({'status': status, 'descricao': mensagem, 'user_id': user_id})


class UserPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, *args, **kwargs):
        email = self.request.data.get('email')
        codigo = random.randint(100000, 999999)

        status, mensagem = service.email.email.Email.enviar_email_recuperacao(destinatario=email, codigo=codigo)

        return JsonResponse({'status': status, 'mensagem': mensagem})


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer