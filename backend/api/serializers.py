from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)
from users.models import Subscription, User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class CustomUserSerializer(UserSerializer):
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


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        read_only=True,
        many=True
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class AddIngredientRecipeSerializer(ModelSerializer):
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class CreateRecipeSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise ValidationError(
                'В рецепте должен быть хотя бы один ингредиент!'
            )
        ingredients_list = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            if int(amount) < 1:
                raise ValidationError(
                    {'amount': 'Количество ингредиента должно быть больше 0!'}
                )
            if ingredient['id'] in ingredients_list:
                raise ValidationError(
                    {'ingredient': 'Ингредиенты должны быть уникальными!'}
                )
            ingredients_list.append(ingredient['id'])
        return data

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError('В рецепте не заполнены теги!')
        for tag in tags:
            if tag.id in tags:
                raise ValidationError('Теги должны быть уникальными!')
        return tags

    def validate_image(self, image):
        if not image:
            raise ValidationError('Добавьте картинку рецепта!')
        return image

    def validate_name(self, name):
        if not name:
            raise ValidationError('Не заполнено название рецепта!')
        if self.context.get('request').method == 'POST':
            current_user = self.context.get('request').user
            if Recipe.objects.filter(author=current_user, name=name).exists():
                raise ValidationError(
                    'Рецепт с таким названием у вас уже есть!'
                )
        return name

    def validate_text(self, text):
        if not text:
            raise ValidationError('Не заполнено описание рецепта!')
        return text

    def validate_cooking_time(self, cooking_time):
        if not cooking_time:
            raise ValidationError('Не заполнено время приготовления рецепта!')
        if int(cooking_time) <= 0:
            raise ValidationError(
                'Убедитесь, что время приготовления больше либо равно 1.'
            )
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        if ingredients:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if tags:
            instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeMinifiedSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
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
        return RecipeMinifiedSerializer(recipes, many=True).data
