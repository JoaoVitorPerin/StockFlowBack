# Generated by Django 5.1.3 on 2024-11-26 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]