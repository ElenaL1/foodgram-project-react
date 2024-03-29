from colorfield.fields import ColorField

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиенты."""
    name = models.CharField('название', max_length=200)
    measurement_unit = models.CharField('единицы измерения', max_length=200)

    class Meta:
        ordering = ("name",)
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'[
            :settings.MAX_LINE_LENGTH]


class Tag(models.Model):
    """Модель теги."""
    name = models.CharField('название', unique=True, max_length=200)
    color = ColorField('цвет в HEX', unique=True)
    slug = models.SlugField('уникальный слаг', unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "тег"
        verbose_name_plural = "теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепты."""
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(Tag, verbose_name="теги",)
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name="картинка",
        help_text="Загрузите картинку"
    )
    name = models.CharField(
        'название',
        max_length=200,
    )
    text = models.TextField('описание')
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления (в минутах)',
        validators=[
            MinValueValidator(settings.MIN_COOKING_TIME,
                              'Время приготовления должно быть больше нуля'),
            MaxValueValidator(settings.MAX_COOKING_TIME,
                              f'Время приготовления не должно превышать\
                              {settings.MAX_COOKING_TIME} мин.')]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="автор",
        related_name="recipes"
    )
    is_favorited = models.ManyToManyField(
        User,
        through='Favorite',
        verbose_name='рецепт добавлен в избранное',
        related_name="is_favorited")
    is_in_shopping_cart = models.ManyToManyField(
        User,
        through='ShoppingCart',
        verbose_name='рецепт добавлен в список покупок',
        related_name="is_in_shopping_cart")
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )

    def times_favorited(self):
        return self.is_favorited.count()
    times_favorited.short_description = 'Число добавлений рецепта в избранное'

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"
        UniqueConstraint(fields=['author', 'name'],
                         name='unique_author_recipe')

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Вспомогательная модель, связывающая рецепты и игредиенты."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredient')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name="ингредиент",)
    amount = models.PositiveSmallIntegerField(
        'количество', validators=[MinValueValidator(
            settings.MIN_INGREDIENT_AMOUNT,
            'Количество ингредиентов не может быть нулевым')])

    class Meta:
        verbose_name = "ингредиент рецепта"
        verbose_name_plural = "ингредиенты рецепта"
        UniqueConstraint(fields=['recipe', 'ingredient'],
                         name='unique_recipe_ingredient')


class ShoppingCart(models.Model):
    """Модель для списока покупок"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепты',
        related_name='recipe_in_shopping_cart')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='владелец корзины',
        related_name='user_shopping_cart')
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "список покупок"
        verbose_name_plural = "список покупок"
        UniqueConstraint(fields=['user', 'recipe'],
                         name='unique_shoppingcart_recipe')


class Favorite(models.Model):
    """Вспомогательная модель,
    связывающая пользователя и понравившиеся им рецепты в избранном.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_favorited',
        verbose_name='рецепт')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorited',
        verbose_name='пользователь, добавивший рецепт в избранное',
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ("recipe",)
        verbose_name = "добавлен в избанное"
        verbose_name_plural = "добавлен в избранное"
        UniqueConstraint(fields=['user', 'recipe'],
                         name='unique_favorite_recipe')
