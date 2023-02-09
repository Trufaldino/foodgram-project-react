from django.contrib.auth import get_user_model
from django.db import models
from users.models import User


class Recipe(models.Model):

    """
        Автор публикации (пользователь).
        Название.
        Картинка.
        Текстовое описание.
        Ингредиенты: продукты для приготовления блюда по рецепту. Множественное поле, выбор из предустановленного списка, с указанием количества и единицы измерения.
        Тег (можно установить несколько тегов на один рецепт, выбор из предустановленных).
        Время приготовления в минутах.
        Все поля обязательны для заполнения.
    """

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
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )  # Ингредиенты: продукты для приготовления блюда по рецепту. Множественное поле, выбор из предустановленного списка, с указанием количества и единицы измерения.
    tag = models.ManyToManyField(
        'Tag',
        verbose_name='Тег',
    )  # Тег (можно установить несколько тегов на один рецепт, выбор из предустановленных).
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
    clolor = models.CharField(
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
        ordering = ['title',]

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'


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
        ordering = ['title',]

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


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