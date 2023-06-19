import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction

from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscribe
from .utils import UserCreateMixin

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Subscribe.objects.filter(following=obj, user=request.user
                                             ).exists())


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации о добавленном рецепте .
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubsribeUserSerializer(CustomUserSerializer):
    """Сериализатор для выдачи пользователей, на которых подписан текущий
    пользователь. В выдачу добавляются рецепты.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Subscribe.objects.filter(following=obj, user=request.user
                                             ).exists())

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class CustomUserCreateSerializer(UserCreateMixin, serializers.ModelSerializer):
    """Сериализатор Django по умолчанию для корректного сохранения пароля.
    """
    password = serializers.CharField(style={"input_type": "password"},
                                     write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def validate(self, data):
        if not data.get('last_name'):
            raise serializers.ValidationError('Нужно указать фамилию.')
        if not data.get('first_name'):
            raise serializers.ValidationError('Нужно указать имя.')
        return data


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

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта и списка рецептов.
    """
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
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

    def to_representation(self, instance):
        self.fields.pop('ingredients')
        self.fields['tags'] = TagSerializer(many=True)
        representation = super().to_representation(instance)
        representation['ingredients'] = RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=instance).all(), many=True
            ).data
        return representation


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
                    f'Такого ингредиента {ingredient} нет в базе.')
        if not data.get('tags'):
            raise serializers.ValidationError(
                'Нужно указать тег.')
        inrgedients_list = [
            ingredient['ingredient'].id for ingredient in data.get(
                'ingredients')]
        if len(inrgedients_list) != len(set(inrgedients_list)):
            raise serializers.ValidationError(
                'Такой ингредиент уже есть в рецепте.')
        tag_list = [tag.id for tag in data.get('tags')]
        if len(tag_list) != len(set(tag_list)):
            raise serializers.ValidationError('Такой тег уже есть в рецепте.')
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Функция сохранения в базе при создании рецепта.
        """
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
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
        instance.tags.clear()
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'])
        instance.save()
        return instance

    def to_representation(self, instance):
        self.fields.pop('ingredients')
        self.fields['tags'] = TagSerializer(many=True)
        representation = super().to_representation(instance)
        representation['ingredients'] = RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=instance).all(), many=True
            ).data
        return representation
