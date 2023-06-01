from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Subscribe, Tag


class RecipeAdmin(admin.ModelAdmin):
    # list_display = ('pk', 'ingredients', 'tags', 'image', 'name',
                    # 'text', 'cooking_time', 'author')
    # list_editable = ('group',)
    # search_fields = ('author', 'tags')
    # list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
#    Перечисляем поля, которые должны отображаться в админке
    # list_display = ('text', 'pub_date', 'author') 
    # Добавляем интерфейс для поиска по тексту постов
    # search_fields = ('text',) 
    # Добавляем возможность фильтрации по дате
    # list_filter = ('pub_date',) 


class SubcribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    list_editable = ('user', 'following')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Favorite)
admin.site.register(Subscribe)
admin.site.register(ShoppingCart)
