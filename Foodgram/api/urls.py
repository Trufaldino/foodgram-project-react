from django.urls import include, path
from rest_framework import routers
from djoser.views import TokenCreateView, TokenDestroyView

from .views import *


router_v1 = routers.DefaultRouter()
router_v1.register(r'users', OwnUserViewSet, basename='users')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingridients', IngredientViewSet, basename='ingridients')

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionListView.as_view(),
        name='subscriptions'
    ),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
    path('', include(router_v1.urls)),
]
