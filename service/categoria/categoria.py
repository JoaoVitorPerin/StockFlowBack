from categoria.models import Categoria

class CategoriasSistema():
    def lista_categorias(self, categoria_id=None):
        try:
            if categoria_id:
                marca = Categoria.objects.filter(id=categoria_id).first()
                if not marca:
                    return False, 'Categoria não encontrada!', []
                lista_categorias = {
                    "id": marca.id,
                    "nome": marca.nome,
                }
            else:
                lista_categorias = list(
                    Categoria.objects.all().values('id', 'nome')
                )

            return True, 'Categorias retornadas com sucesso', lista_categorias
        except Exception as e:
            return False, str(e), []

    def cadastrar_categoria(self, categoria_id=None, nome=None):
        try:
            if not categoria_id:
                categoria_existente = Categoria.objects.filter(nome__iexact=nome).first()

                if categoria_existente:
                    return False, 'Categoria já cadastrada!', None

                nova_categoria = Categoria(
                    nome=nome,
                )
                nova_categoria.save()

                return True, 'Categoria cadastrada com sucesso!', nova_categoria.id
            else:
                categoria = Categoria.objects.filter(id=categoria_id).first()
                if not categoria:
                    return False, 'Categoria não encontrada!', None

                categoria.nome = nome
                categoria.save()

                return True, 'Categoria atualizada com sucesso!', categoria.id
        except Exception as e:
            return False, str(e), None