from django.db import models

class CustoMensal(models.Model):
    nome = models.CharField(max_length=255, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    dat_ini = models.DateTimeField(max_length=30, null=True)
    dat_fim = models.DateTimeField(max_length=30, null=True)
    recorrente = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.nome