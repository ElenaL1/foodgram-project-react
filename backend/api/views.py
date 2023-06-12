# from django.shortcuts import render
from rest_framework import viewsets
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
# from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import filters, permissions, response, status, viewsets
# from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from http import HTTPStatus
from djoser.views import UserViewSet

from .filters import RecipeFilter
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Subscribe

from .serializers import (IngredientSerializer, FavoriteSerializer,
                          RecipeSerializer, RecipeCreateSerializer,
                          ShoppingCartSerializer,
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
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class ShoppingCartView(APIView):

    def post(self, request):
        user = self.request.user
        serializer = ShoppingCartSerializer(data=request.data)
        if not user.is_authenticated:
            return Response(
                serializer.error, status=HTTPStatus.UNAUTHORIZED)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=HTTPStatus.BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)

    def get(self, request):
        is_favorited = Favorite.user_favorited(
            user=self.request.user, recipe=self.request.recipe)
        serializer = FavoriteSerializer(is_favorited, many=True)
        return Response(serializer.data)

    def delete(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class DownloadShoppingCart(APIView):
    ...


class FavoriteView(APIView):

    def post(self, request):
        user = self.request.user
        serializer = FavoriteSerializer(data=request.data, many=True)
        if not user.is_authenticated:
            return Response(
                serializer.error, status=HTTPStatus.UNAUTHORIZED)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=HTTPStatus.BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


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
