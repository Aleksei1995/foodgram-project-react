from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe', )
    fields = (('recipe',), ('ingredient', 'amount'))
    list_editable = ('amount', )
    list_display_links = ('id', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    def count_favorites(self, object):
        return object.favorites.count()


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
