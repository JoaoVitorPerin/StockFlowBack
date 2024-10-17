from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    codigo_reset = models.IntegerField(null=True)
    validade_codigo = models.DateTimeField(null=True)
    role = models.CharField(max_length=100, null=True)