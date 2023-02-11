from django.db import models
from users.models import User


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название блюда',
    )
    image = models.ImageField(
        upload_to='recipes/images',
        blank=True,
        null=True,
        verbose_name='Картинка',
    )
    description = models.TextField(
        verbose_name='Текстовое описание',
    )
    ingredient = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tag = models.ManyToManyField(
        'Tag',
        verbose_name='Тег',
    )
    time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        unique=True,
    )
    color = models.CharField(
        max_length=50,
        verbose_name='цвет',
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='слаг',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} (цвет: {self.color})'


class Ingredient(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название ингридиента',
    )
    unit = models.IntegerField(
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['title']

    def __str__(self) -> str:
        return f'{self.title} {self.unit}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredient_of_recipe',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='ingredient_of_recipe',
        verbose_name='Ингредиент'
    )
    quantity = models.IntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.ingredient} {self.quantity}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Shoppinglist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} {self.recipe}'
