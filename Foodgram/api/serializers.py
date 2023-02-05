from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from recipes.models import *


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = "__all__"