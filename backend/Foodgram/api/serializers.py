from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shoppinglist, Tag)
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField)
from users.models import Subscription, User


class OwnUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ['email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password']


class OwnUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ['email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed']

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return not user.is_anonymous and Subscription.objects.filter(
            user=user,
            author=author.id
        ).exists()


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id',
                  'title',
                  'color',
                  'slug']


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id',
                  'title',
                  'unit']


class Recipeingredienterializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.title')
    unit = ReadOnlyField(source='ingredient.unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id',
                  'name',
                  'unit',
                  'quantity']


class RecipeSerializer(ModelSerializer):
    tag = TagSerializer(read_only=True, many=True)
    author = OwnUserSerializer(read_only=True)
    ingredient = Recipeingredienterializer(
        source='ingredient_of_recipe',
        read_only=True,
        many=True
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id',
                  'tag',
                  'author',
                  'ingredient',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'title',
                  'image',
                  'description',
                  'time']

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


class PostIngredientRecipeSerializer(ModelSerializer):
    id = IntegerField()
    quantity = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id',
                  'quantity']


class CreateRecipeSerializer(ModelSerializer):
    author = OwnUserSerializer(read_only=True)
    ingredient = PostIngredientRecipeSerializer(many=True)
    tag = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredient',
            'tag',
            'image',
            'title',
            'description',
            'time',
        ]

    def create_ingredient(self, ingredient, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                quantity=ingredient['quantity']
            ) for ingredient in ingredient]
        )

    def create(self, validated_data):
        ingredient = validated_data.pop('ingredient')
        tag = validated_data.pop('tag')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredient(ingredient, recipe)
        recipe.tag.set(tag)
        return recipe

    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredient = validated_data.pop('ingredient')
        tag = validated_data.pop('tag')
        instance = super().update(instance, validated_data)
        if ingredient:
            instance.ingredient.clear()
            self.create_ingredient(ingredient, instance)
        if tag:
            instance.tag.set(tag)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeSmallSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id',
                  'title',
                  'image',
                  'time']


class SubscriptionSerializer(OwnUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, author):
        return author.recipes.count()

    def get_recipes(self, author):
        recipes = author.recipes.all()
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit'
        )
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
