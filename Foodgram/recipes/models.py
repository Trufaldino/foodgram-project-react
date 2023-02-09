from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


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
        verbose_name='Название',
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        null=True,
        verbose_name='Картинка',
    )
    description = models.TextField(
        verbose_name='Текстовое описание',
    )
    ingredients = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
    )  # Ингредиенты: продукты для приготовления блюда по рецепту. Множественное поле, выбор из предустановленного списка, с указанием количества и единицы измерения.
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE,
        verbose_name='Тег',
    )  # Тег (можно установить несколько тегов на один рецепт, выбор из предустановленных).
    time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
    )

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    clolor = models.CharField(
        max_length=200,
        verbose_name='цвет',
    )
    unit = models.SlugField(
        verbose_name='slug',
    )


class Ingredient(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    quantity = models.IntegerField(
        verbose_name='Колличество',
    )
    unit = models.IntegerField(
        verbose_name='Единица измерения',
    )
