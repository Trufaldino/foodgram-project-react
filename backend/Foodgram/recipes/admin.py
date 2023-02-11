from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     Shoppinglist, Tag)


@admin.register(Recipe)
class RecipeModelAdmin(admin.ModelAdmin):
    list_display = ('author', 'id', 'title', 'count_in_favorites')
    readonly_fields = ('count_in_favorites',)
    list_filter = ('author', 'title', 'tag',)

    def count_in_favorites(self, recipe):
        return Favorite.objects.filter(recipe=recipe).count()


@admin.register(Ingredient)
class IngredientModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit',)
    list_filter = ('unit',)


@admin.register(Tag)
class TagModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'color', 'slug',)


@admin.register(Shoppinglist)
class ShoppinglsitModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Favorite)
class FavouriteModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(RecipeIngredient)
class RecipeIngredientModelAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'quantity',)
