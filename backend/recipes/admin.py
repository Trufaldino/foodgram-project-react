from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'count_in_favorites')
    list_filter = ('author', 'name', 'tags')
    inlines = (RecipeIngredientInline, )

    def count_in_favorites(self, recipe):
        return Favorite.objects.filter(recipe=recipe).count()


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
