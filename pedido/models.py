from django.db import models
from cliente.models import Cliente
from produto.models import Produto

class Pedido(models.Model):
    idPedido = models.AutoField(primary_key=True)
    dataPedido = models.DateField(null=False)
    vlrTotal = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

class ItemPedido(models.Model):
    idItemPedido = models.AutoField(primary_key=True)
    quantidade = models.IntegerField(null=False)
    precoUnitario = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)