from django.contrib import admin
from django.urls import path
from user import urls as user_urls
from django.urls import re_path, include

urlpatterns = [
    path('user/', include('user.urls')),
]
