# Generated by Django 5.1.5 on 2025-02-02 01:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0011_produto_preco_venda_real'),
    ]

    operations = [
        migrations.RenameField(
            model_name='produto',
            old_name='preco_venda_real',
            new_name='preco_compra_real',
        ),
    ]
