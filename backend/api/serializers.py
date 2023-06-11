import base64
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import serializers
from django.core.files.base import ContentFile
# from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Subscribe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Subscribe.objects.filter(
            following=obj,
            user=user
        ).exists()


class UserCreateMixin:
    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")
        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
        return user


class CustomUserCreateSerializer(UserCreateMixin, serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"},
                                     write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class Base64ImageField(serializers.ImageField):
    """Сериализатор для картинки.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для игредиентов.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов.
    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug', )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации об ингредиентах.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class RecipeIngredientShortSerializer(serializers.ModelSerializer):
    """Сериализатор для ввода информации об ингредиентах.
    """
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            queryset=Ingredient.objects.all())
    # id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    # amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта и списка рецептов.
    """
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    # ingredients = RecipeIngredientSerializer(
    #     many=True, read_only=True, source='recipes')
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_ingredients(self, obj):
        """Определение ингредиентов в рецепте."""
        recipe = obj
        queryset = recipe.recipe_ingredient.all()
        return RecipeIngredientSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        """Проверка есть ли рецепт в избранном."""
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.user_favorited.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """Проверка есть ли рецепт в списке покупок."""
        request = self.context.get('request')
        return (request and request.user.is_authenticated and
                request.user.is_in_shopping_cart.filter(recipe=obj).exists())

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',  'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, изменения и удаления рецепта.
    """
    ingredients = RecipeIngredientShortSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate(self, data):
        if not data.get('ingredients'):
            raise serializers.ValidationError(
                'Нужно указать один ингредиент.'
            )
        for ingredient in data.get('ingredients'):
            if not Ingredient.objects.filter(
                    id=ingredient['ingredient'].id).exists():
                raise serializers.ValidationError(
                    f'Такого ингредиента {ingredient} не существует.\
                    Сначала добавьте ингредиент в базу')
        # inrgedients_list = [item['id'] for item in data.get('ingredients')]
        # if len(inrgedients_list) != len(set(inrgedients_list)):
        #     raise serializers.ValidationError(
        #         'Ингредиенты не должны повторяться.')
        if not data.get('tags'):
            raise serializers.ValidationError(
                'Нужно указать тег.')
        # for tag in data.get('tags'):
        #     if not Tag.objects.filter(id=tag.id).exists():
        #         raise serializers.ValidationError(
        #             f'Такого тега {tag} не существует. Сначала добавьте\
        #             тег в базу')
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Функция сохранения в базе при создании рецепта.
        """
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        # recipe.tags.add(**tags_data)
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                # ingredient_id=ingredient['ingredient'].id,
                recipe=recipe,
                # ingredient=Ingredient.objects.get(
                #    pk=ingredient['ingredient'].id),
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'])
        recipe.save()
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Фунция сохранения в базе при обновлении рецепта.
        """
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.tags.clear()  # удалаяем все теги для данного рецепта из связанной таблицы
        instance.tags.add(*tags_data)  # добавляем tag в связанную таблицу
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                # ingredient=ingredient.get('id'),
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient.get('amount'))
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance, context={'request': request}).data


class SubscribeSerializer(serializers.ModelSerializer):
    # is_subscribed = (many=True)
    ...


class ShoppingCartSerializer(serializers.ModelSerializer):
    ...
    # def get_ingredients(self, instance):
    #     """Суммирование ингредиентов в списке покупок."""
    #     result = []
    #     ingredients = instance.ingredients.get_queryset()
    #     print(instance)
    #     for ingredient in ingredients:
    #         data = IngredientSerializer(ingredient).data
    #         data['amount'] = RecipeIngredient.objects.filter(
    #             recipe=instance, ingredient=ingredient
    #         ).first().amount
    #         result.append(data)
    #     return result
