from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from StockFlowBack.serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import service.user.user

class UserCadastoView(APIView):
    def post(self, *args, **kwargs):
        username = self.request.data.get('username')
        password = 'Stockflow@2024'
        nome = self.request.data.get('first_name')
        sobrenome = self.request.data.get('last_name')
        email = self.request.data.get('email')

        status, mensagem, user_id = service.user.user.Usuario(username=username, password=password).cadastrar_usuario(nome=nome,
                                                                                                              sobrenome=sobrenome,
                                                                                                              email=email)

        return JsonResponse({'status': status, 'descricao':mensagem, 'user_id': user_id})

class GestaoUsuarioView(APIView):
    def get(self, *args, **kwargs):
        user_id = self.request.GET.get('user_id')
        status, mensagem, usuarios = service.user.user.Usuario().listar_usuarios(user_id=user_id)
        return JsonResponse({'status': status, 'mensagem': mensagem, 'usuario': usuarios})

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer