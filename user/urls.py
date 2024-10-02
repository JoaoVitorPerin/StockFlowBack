from django.urls import re_path, include
from user.views import UserCadastoView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    re_path(r'^login$', TokenObtainPairView.as_view()),
    re_path(r'^cadastro$', UserCadastoView.as_view()),
]