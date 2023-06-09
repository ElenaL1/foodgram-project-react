from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.CharFilter(field_name='is_favorited__slug',)
    tags = filters.CharFilter(field_name='tag__slug',)
    is_in_shopping_cart = filters.CharFilter(
        field_name='shopping_cart__author',)

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'author', 'is_in_shopping_cart', 'tags')
