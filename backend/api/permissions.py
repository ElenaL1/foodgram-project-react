from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает анонимному пользователю только безопасные запросы.
    Полный доступ у авторизованнорго пользователя с ролью
    администратор.
    """
    message = 'Доступ только у администратора.'

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_admin))


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает анонимному пользователю только безопасные запросы.
    Полный доступ у авторизованнорго пользователя.
    """
    message = 'Доступ только у авторизованного пользователя.'

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
