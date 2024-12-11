from django.db import models

class Cotacao(models.Model):
    valor = models.FloatField(null=True)
    data = models.DateTimeField(auto_now=True)