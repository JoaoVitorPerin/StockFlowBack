# Generated by Django 5.1.3 on 2024-12-11 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cotacao',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('valor', models.FloatField(null=True)),
                ('data', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
