from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views

from .views import *


router_v1 = routers.DefaultRouter()
router_v1.register(r'recipes', RecipeViewSet)
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'ingridients', IngredientViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
]
