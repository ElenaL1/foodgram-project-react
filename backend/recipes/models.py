from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('название', max_length=200)
    measurement_unit = models.CharField('единицы измерения', max_length=200)

    class Meta:
        ordering = ("name",)
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField('название', unique=True, max_length=200)
    color = models.CharField('цвет в HEX', unique=True, max_length=7, null=True)
    slug = models.SlugField('уникальный слаг', unique=True, null=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "тег"
        verbose_name_plural = "теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(Tag)
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
    cooking_time = models.PositiveSmallIntegerField('время приготовления (в минутах)')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="автор",
        related_name="recipes"
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()


class ShoppingCart(models.Model):
    recipes = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        ordering = ("recipes",)
        verbose_name = "список покупок"
        verbose_name_plural = "список покупок"


class Favorite(models.Model):
    recipes = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        ordering = ("recipes",)
        verbose_name = "избранное"
        verbose_name_plural = "избранное"


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="подписчик",
        related_name="follower"
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="автор рецепта",
        related_name="followed"
    )

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
        constraints = [
            UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'),
            CheckConstraint(
                check=~Q(user=F('following')),
                name='unique_following')
        ]
