from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from recipes.models import *
from users.models import *


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = "__all__"

    
class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = "__all__"