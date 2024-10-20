from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50, unique=True)
    categoria = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco_compra = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)
    def __str__(self):
        return self.nome