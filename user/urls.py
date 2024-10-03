from django.urls import re_path, include
from user.views import UserCadastoView, MyTokenObtainPairView

urlpatterns = [
    re_path(r'^login$', MyTokenObtainPairView.as_view()),
    re_path(r'^cadastro$', UserCadastoView.as_view()),
]