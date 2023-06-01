import base64
from rest_framework import serializers
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from recipes.models import Ingredient, User, Recipe


class UserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'username',
                  'first_name', 'last_name', 'password')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    # ingredients = IngredientSerializer(many=True)
    ...


class TagSerializer(serializers.ModelSerializer):
    # tags = TagSerializer(many=True)
    ...


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    # color = Hex2NameColor()
    # Вот оно — новое поле для изображений.
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        # fields = (
        #     'id', 'name', 'color', 'birth_year', 'achievements', 'owner', 'age',
        #     'image'
        # )
        # read_only_fields = ('owner',)