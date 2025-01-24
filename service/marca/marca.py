from marca.models import Marca


class MarcaSistema():
    def listar_marcas(self, marca_id=None):
        try:
            if marca_id:
                marca = Marca.objects.filter(id=marca_id).first()
                if not marca:
                    return False, 'Marca não encontrada!', []
                lista_marcas = {
                    "id": marca.id,
                    "nome": marca.nome,
                }
            else:
                lista_marcas = list(
                    Marca.objects.all().values('id', 'nome')
                )

            return True, 'Marcas retornadas com sucesso', lista_marcas
        except Exception as e:
            return False, str(e), []

    def cadastrar_marca(self, marca_id=None, nome=None):
        try:
            if not marca_id:
                marca_existente = Marca.objects.filter(nome__iexact=nome).first()

                if marca_existente:
                    return False, 'Marca já cadastrada!', None

                nova_marca = Marca(
                    nome=nome,
                )
                nova_marca.save()

                return True, 'Marca cadastrada com sucesso!', nova_marca.id
            else:
                marca = Marca.objects.filter(id=marca_id).first()
                if not marca:
                    return False, 'Marca não encontrada!', None

                marca.nome = nome
                marca.save()

                return True, 'Marca atualizada com sucesso!', marca.id
        except Exception as e:
            return False, str(e), None