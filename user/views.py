from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from StockFlowBack.serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import service.user.user

class UserCadastoView(APIView):
    def get_permissions(self):
        """
        Instancia e retorna a lista de permissões que essa view requer.
        """
        if self.request.method == 'POST':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    def post(self, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        nome = self.request.data.get('nome')
        sobrenome = self.request.data.get('sobrenome')
        email = self.request.data.get('email')

        status, mensagem = service.user.user.Usuario(username=username, password=password).cadastrar_usuario(nome=nome,
                                                                                                              sobrenome=sobrenome,
                                                                                                              email=email)

        return JsonResponse({'status': status, 'descricao':mensagem})

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer