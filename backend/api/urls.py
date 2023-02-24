from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet,  # isort:skip
                    RecipeViewSet, SubscriptionListView, TagViewSet)


router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionListView.as_view(),
        name='subscriptions'
    ),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
    path('', include(router.urls))
]
