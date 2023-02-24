from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Subscription, User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import LimitPagination
from .permissions import IsAuthor, IsReadOnly
from .serializers import (CreateRecipeSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeMinifiedSerializer,
                          RecipeSerializer, SubscriptionSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    pagination_class = LimitPagination

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        return super(CustomUserViewSet, self).me(request, *args, **kwargs)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'Нельзя подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscription.objects.filter(
                user=user, author=author
        ).exists():
            return Response(
                {'Нельзя подписаться повторно!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.create(
            user=user,
            author=author
        )
        serializer = SubscriptionSerializer(
            author,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'Попытка удалить несуществующую подписку!'},
            status=status.HTTP_400_BAD_REQUEST
        )


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter, ]
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthor | IsReadOnly]
    pagination_class = LimitPagination
    filter_backends = [DjangoFilterBackend, ]
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    def execution(self, request, pk, attr):
        instance = attr.objects.filter(user=request.user, recipe__id=pk)
        if request.method == 'POST' and not instance.exists():
            recipe = get_object_or_404(Recipe, id=pk)
            attr.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE' and instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.execution(request, pk, Favorite)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.execution(request, pk, ShoppingCart)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        shopping_list = ['{} ({}) - {}\n'.format(
            ingredient['ingredient__name'],
            ingredient['ingredient__measurement_unit'],
            ingredient['total_amount']
        ) for ingredient in ingredients]
        response = HttpResponse(shopping_list, content_type='text/plain')
        attachment = 'attachment; filename="shopping_list.txt"'
        response['Content-Disposition'] = attachment
        return response


class SubscriptionListView(ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitPagination

    def get_queryset(self):
        return User.objects.filter(subscriptions__user=self.request.user)
