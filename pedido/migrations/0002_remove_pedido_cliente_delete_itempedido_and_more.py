# Generated by Django 5.1.3 on 2024-11-30 01:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pedido', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='cliente',
        ),
        migrations.DeleteModel(
            name='ItemPedido',
        ),
        migrations.DeleteModel(
            name='Pedido',
        ),
    ]
