from django.core.exceptions import PermissionDenied
from functools import wraps

def group_required(*group_names):
    """
    Decorator para verificar se o usuário pertence a um ou mais grupos.
    :param group_names: Lista de grupos que têm permissão para acessar a view
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return _wrapped_view
    return decorator
