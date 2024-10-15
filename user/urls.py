from django.urls import re_path, include
from user.views import UserCadastoView, MyTokenObtainPairView, UserPasswordResetView

urlpatterns = [
    re_path(r'^login$', MyTokenObtainPairView.as_view()),
    re_path(r'^cadastro$', UserCadastoView.as_view()),
    re_path(r'^gestao$', UserCadastoView.as_view()),
    re_path(r'^enviar_email_reset$', UserPasswordResetView.as_view()),
]