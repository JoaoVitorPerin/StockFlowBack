from django.db import models


class Cliente(models.Model):
    # Campos principais
    nome_completo = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=18, unique=True, null=True)
    telefone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True, null=True)

    # Endereço
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=255, null=True, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)

    status = models.BooleanField(default=True)

    # Outras informações
    indicacao = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='indicados'
    )
    is_atleta = models.BooleanField(default=False, null=True)
