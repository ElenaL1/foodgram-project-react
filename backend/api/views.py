from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscribe

from .filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          SubsribeUserSerializer, TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticated,)

    @action(detail=False, pagination_class=CustomPagination)
    def subscriptions(self, request):
        queryset = User.objects.filter(followed__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubsribeUserSerializer(page, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            if Subscribe.objects.filter(
                    user=request.user,
                    following=author) or request.user == author:
                return Response(status=HTTPStatus.BAD_REQUEST)
            Subscribe.objects.create(user=request.user, following=author)
            serializer = SubsribeUserSerializer(
                author, context={"request": request})
            return Response(serializer.data, status=HTTPStatus.CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscribe, user=request.user,
                              following=author).delete()
            return Response(status=HTTPStatus.NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    # filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            if not Favorite.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
                serializer = RecipeShortSerializer(
                    instance=recipe, context={"request": request})
                return Response(serializer.data, status=HTTPStatus.CREATED)
            return Response(status=HTTPStatus.BAD_REQUEST)
        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                user=request.user, recipe=recipe)
            if favorite:
                favorite.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            return Response(status=HTTPStatus.BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            if not ShoppingCart.objects.filter(
                    user=request.user, recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                serializer = RecipeShortSerializer(
                    instance=recipe, context={"request": request})
                return Response(serializer.data, status=HTTPStatus.CREATED)
            return Response(status=HTTPStatus.BAD_REQUEST)
        if request.method == 'DELETE':
            shoppingcart = ShoppingCart.objects.filter(
                user=request.user, recipe=recipe)
            if shoppingcart:
                shoppingcart.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            return Response(status=HTTPStatus.BAD_REQUEST)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__recipe_in_shopping_cart__user=user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name',
                         'ingredient__measurement_unit',
                         'total_amount'))
        file_data = [f'Список покупок пользователя: {user}']
        for ingredient in ingredients:
            # ingredient[0] = ingredient[0].capitalize()
            file_data.append(
                f'{ingredient[0]} ({ingredient[1]}) - {ingredient[2]}'
                )
        response = HttpResponse('\n'.join(file_data).capitalize(),
                                content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"')
        return response
