# from django.shortcuts import render
from rest_framework import viewsets
from djoser.views import UserViewSet

from recipes.models import Ingredient, Recipe, Tag, User
from .serializers import (IngredientSerializer, UserSerializer,
                          RecipeSerializer, TagSerializer)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    # def validate(self, data):
    #     if data['color'] == data['name']:
    #         raise serializers.ValidationError(
    #             'Имя не может совпадать с цветом!')
    #     return data

# class CommentViewSet(viewsets.ModelViewSet):
#     serializer_class = CommentSerializer
#     # queryset во вьюсете не указываем
#     # Нам тут нужны не все комментарии, а только связанные с котом с id=cat_id
#     # Поэтому нужно переопределить метод get_queryset и применить фильтр
#     def get_queryset(self):
#         # Получаем id котика из эндпоинта
#         cat_id = self.kwargs.get("cat_id")
#         # И отбираем только нужные комментарии
#         new_queryset = Comment.objects.filter(cat=cat_id)
#         return new_queryset
