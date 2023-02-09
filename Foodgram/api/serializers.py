from djoser.serializers import UserCreateSerializer, UserSerializer
# from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (IntegerField, 
                                        ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        ReadOnlyField,
                                        SerializerMethodField,
                                        ValidationError)

from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            Favorite, 
                            Shoppinglist)
from users.models import Subscription, User


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 
                  'id', 
                  'username', 
                  'first_name', 
                  'last_name',
                  'password'
        )


class UserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return not user.is_anonymous and Subscription.objects.filter(
            user=user,
            author=author.id
        ).exists()

    
class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'title', 'color', 'slug')


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'unit')


class RecipeIngredientSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.title')
    measurement_unit = ReadOnlyField(source='ingredient.unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'unit', 'quantity')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredient_of_recipe',
        read_only=True,
        many=True
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tag', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'title', 'image', 'description',
                  'time')

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Shoppinglist.objects.filter(user=user, recipe=recipe).exists()