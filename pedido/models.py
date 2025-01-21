from django.db import models
from cliente.models import Cliente
from produto.models import Produto

class Pedido(models.Model):
    idPedido = models.AutoField(primary_key=True)
    dataPedido = models.DateField(null=False)
    vlrTotal = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    frete = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    # Campos de endereço
    logradouro = models.CharField(max_length=255, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=255, null=True, blank=True)
    bairro = models.CharField(max_length=255, null=True, blank=True)
    localidade = models.CharField(max_length=255, null=True, blank=True)
    uf = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=15, null=True, blank=True)


class ItemPedido(models.Model):
    idItemPedido = models.AutoField(primary_key=True)
    quantidade = models.IntegerField(null=False)
    is_estoque_externo = models.BooleanField(default=False)
    precoUnitario = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)