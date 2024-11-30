# Generated by Django 5.1.3 on 2024-11-30 01:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cliente', '0003_alter_cliente_telefone'),
        ('produto', '0007_estoque_usuario_movimentacaoestoque_usuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('idPedido', models.AutoField(primary_key=True, serialize=False)),
                ('dataPedido', models.DateField()),
                ('vlrTotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('desconto', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cliente.cliente')),
            ],
        ),
        migrations.CreateModel(
            name='ItemPedido',
            fields=[
                ('idItemPedido', models.AutoField(primary_key=True, serialize=False)),
                ('quantidade', models.IntegerField()),
                ('precoUnitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='produto.produto')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='pedido.pedido')),
            ],
        ),
    ]
