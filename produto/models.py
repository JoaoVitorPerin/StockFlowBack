from django.db import models

from marca.models import Marca
from user.models import Usuario

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name="produtos", null=True)
    descricao = models.TextField(blank=True, null=True)
    preco_compra = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)
    def __str__(self):
        return self.nome

class Estoque(models.Model):
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(null=True)
    data_ultima_movimentacao = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Estoque de {self.produto.nome}'

class MovimentacaoEstoque(models.Model):
    TIPOS_MOVIMENTACAO = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=True)
    tipo = models.CharField(max_length=10, choices=TIPOS_MOVIMENTACAO, null=True)
    quantidade = models.IntegerField(null=True)
    data_movimentacao = models.DateTimeField(null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.tipo.capitalize()} - {self.produto.nome} - {self.data_movimentacao}'


class Cliente:
    pass