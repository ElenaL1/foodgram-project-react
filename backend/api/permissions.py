from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает анонимному пользователю только безопасные запросы.
    Полный доступ у авторизованнорго пользователя к своему контенту.
    """
    message = 'Доступ только у авторизованного пользователя.'

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)
