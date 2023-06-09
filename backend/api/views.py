# from django.shortcuts import render
from rest_framework import viewsets
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
# from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import filters, permissions, response, status, viewsets
# from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet

from .filters import RecipeFilter
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Subscribe

from .serializers import (IngredientSerializer,
                          RecipeSerializer, RecipeCreateSerializer,
                          SubscribeSerializer, TagSerializer)
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    # permission_classes = (IsAuthorOrReadOnly,)
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    # filterset_class = RecipeFilter
    # search_fields = ('name',)
    # pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        if self.action == 'list' or 'retrieve':
            return RecipeSerializer

    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     context.update({'request': self.request})
    #     return context

    # def validate(self, data):
    #     if data['color'] == data['name']:
    #         raise serializers.ValidationError(
    #             'Имя не может совпадать с цветом!')
    #     return data

# class CommentViewSet(viewsets.ModelViewSet):
#     serializer_class = CommentSerializer
#     # queryset во вьюсете не указываем
#     # Нам тут нужны не все комментарии,
#     # а только связанные с котом с id=cat_id
#     # Поэтому нужно переопределить метод get_queryset и применить фильтр
#     def get_queryset(self):
#         # Получаем id котика из эндпоинта
#         cat_id = self.kwargs.get("cat_id")
#         # И отбираем только нужные комментарии
#         new_queryset = Comment.objects.filter(cat=cat_id)
#         return new_queryset
