# Generated by Django 5.1.4 on 2025-01-26 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedido', '0006_alter_pedido_datapedido'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='status',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
