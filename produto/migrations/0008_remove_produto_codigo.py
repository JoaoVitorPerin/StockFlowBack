# Generated by Django 5.1.4 on 2025-01-21 01:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0007_estoque_usuario_movimentacaoestoque_usuario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produto',
            name='codigo',
        ),
    ]
