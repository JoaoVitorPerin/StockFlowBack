from django.contrib.auth.models import Group, Permission

def run():
    # Criação dos grupos e permissões como no exemplo anterior
    admin_group, created = Group.objects.get_or_create(name='Administrador')
    operador_group, created = Group.objects.get_or_create(name='Operador de Estoque')
    visualizador_group, created = Group.objects.get_or_create(name='Visualizador')

    # Adicionar permissões ao grupo Administrador
    admin_group.permissions.add(
        *Permission.objects.filter(codename__in=[
            'add_usuario', 'change_usuario', 'delete_usuario'
        ])
    )

    # Adicionar permissões ao grupo Operador de Estoque
    # operador_group.permissions.add(
    #     *Permission.objects.filter(codename__in=[
    #         'add_produto', 'change_produto'
    #     ])
    # )

    # Adicionar permissões ao grupo Visualizador
    # visualizador_group.permissions.add(
    #     Permission.objects.get(codename='view_produto')
    # )
    print("Grupos e permissões configurados com sucesso.")
